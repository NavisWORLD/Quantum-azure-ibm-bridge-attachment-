//! Native Rust implementation of the Quantum Bridge Transformer (QBT).
//!
//! QBT keeps quantum execution, normalization/provenance, and classical
//! model/control consumption separate. Provider failures are isolated and the
//! normalized control state remains bounded.

use std::collections::BTreeMap;
use std::env;
use std::fs;
use std::path::{Path, PathBuf};

use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use thiserror::Error;

#[derive(Debug, Error)]
pub enum QbtError {
    #[error("configuration error: {0}")]
    Config(String),
    #[error("provider error: {0}")]
    Provider(String),
    #[error("invalid provider result: {0}")]
    InvalidResult(String),
    #[error("operation timed out: {0}")]
    Timeout(String),
    #[error(transparent)]
    Io(#[from] std::io::Error),
    #[error(transparent)]
    Http(#[from] reqwest::Error),
    #[error(transparent)]
    Json(#[from] serde_json::Error),
}

pub type Result<T> = std::result::Result<T, QbtError>;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum ExecutionMode {
    Hardware,
    Simulator,
    Archive,
    Fallback,
}

impl ExecutionMode {
    pub fn as_str(self) -> &'static str {
        match self {
            Self::Hardware => "hardware",
            Self::Simulator => "simulator",
            Self::Archive => "archive",
            Self::Fallback => "fallback",
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Quality {
    pub quality_class: String,
    pub confidence: Option<f64>,
}

impl Default for Quality {
    fn default() -> Self {
        Self {
            quality_class: "unknown".to_string(),
            confidence: None,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct QuantumSample {
    pub provider: String,
    pub backend: String,
    pub mode: ExecutionMode,
    pub counts: BTreeMap<String, u64>,
    pub shots: u64,
    pub job_id: Option<String>,
    pub timestamp: String,
    pub metadata: Value,
    pub quality: Quality,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct QuantumState {
    pub qbt_version: String,
    pub provider: String,
    pub backend: String,
    pub execution_mode: String,
    pub timestamp: String,
    pub job_id: Option<String>,
    pub shots: u64,
    pub entropy: f64,
    pub normalized_vector: Vec<f64>,
    pub result_digest: String,
    pub provenance: Value,
    pub quality: Quality,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ControlPacket {
    pub qbt_version: String,
    pub active_sources: usize,
    pub quantum_mix: f64,
    pub states: Vec<QuantumState>,
    pub provider_errors: BTreeMap<String, String>,
}

fn clip01(value: f64) -> f64 {
    if !value.is_finite() {
        return 0.5;
    }
    value.clamp(0.0, 1.0)
}

pub fn entropy_from_counts(counts: &BTreeMap<String, u64>) -> f64 {
    if counts.is_empty() {
        return 0.5;
    }
    let total: u64 = counts.values().copied().sum();
    if total == 0 {
        return 0.5;
    }
    let positive: Vec<u64> = counts
        .values()
        .copied()
        .filter(|value| *value > 0)
        .collect();
    if positive.len() <= 1 {
        return 0.0;
    }

    let mut entropy = 0.0;
    for value in &positive {
        let p = *value as f64 / total as f64;
        entropy -= p * p.log2();
    }
    let max_entropy = (positive.len() as f64).log2();
    clip01(entropy / max_entropy)
}

pub fn canonical_digest<T: Serialize>(value: &T) -> Result<String> {
    let bytes = serde_json::to_vec(value)?;
    let mut hasher = Sha256::new();
    hasher.update(bytes);
    Ok(hex::encode(hasher.finalize()))
}

pub fn normalize_sample(sample: QuantumSample) -> Result<QuantumState> {
    let entropy = entropy_from_counts(&sample.counts);
    let hardware_flag = if sample.mode == ExecutionMode::Hardware {
        1.0
    } else {
        0.0
    };
    let shot_reliability = clip01((sample.shots.max(1) as f64).log2() / 16.0);
    let confidence = clip01(sample.quality.confidence.unwrap_or(0.5));

    let digest_payload = json!({
        "provider": sample.provider,
        "backend": sample.backend,
        "mode": sample.mode.as_str(),
        "counts": sample.counts,
        "shots": sample.shots,
        "job_id": sample.job_id,
        "timestamp": sample.timestamp,
    });
    let result_digest = canonical_digest(&digest_payload)?;

    Ok(QuantumState {
        qbt_version: "1.0".to_string(),
        provider: sample.provider.clone(),
        backend: sample.backend.clone(),
        execution_mode: sample.mode.as_str().to_string(),
        timestamp: sample.timestamp,
        job_id: sample.job_id.clone(),
        shots: sample.shots,
        entropy,
        normalized_vector: vec![entropy, hardware_flag, shot_reliability, confidence],
        result_digest,
        provenance: json!({
            "provider": sample.provider,
            "backend": sample.backend,
            "job_id": sample.job_id,
            "mode": sample.mode.as_str(),
            "metadata": sample.metadata,
        }),
        quality: sample.quality,
    })
}

pub fn blend_quantum_entropy<'a>(
    states: impl IntoIterator<Item = &'a QuantumState>,
    fallback: f64,
) -> f64 {
    let values: Vec<f64> = states
        .into_iter()
        .filter(|state| state.execution_mode != "fallback")
        .map(|state| state.entropy)
        .filter(|value| value.is_finite())
        .collect();

    if values.is_empty() {
        return clip01(fallback);
    }
    clip01(values.iter().sum::<f64>() / values.len() as f64)
}

pub trait QuantumProvider: Send {
    fn name(&self) -> &str;
    fn connect(&mut self) -> Result<()>;
    fn health(&self) -> Value;
    fn sample(&mut self, shots: u64) -> Result<QuantumSample>;
    fn close(&mut self) -> Result<()> {
        Ok(())
    }
}

pub struct QuantumBridge {
    providers: Vec<Box<dyn QuantumProvider>>,
    fallback: f64,
    last_states: Vec<QuantumState>,
    last_errors: BTreeMap<String, String>,
}

impl QuantumBridge {
    pub fn new(providers: Vec<Box<dyn QuantumProvider>>) -> Self {
        Self {
            providers,
            fallback: 0.5,
            last_states: Vec::new(),
            last_errors: BTreeMap::new(),
        }
    }

    pub fn with_fallback(mut self, fallback: f64) -> Self {
        self.fallback = fallback.clamp(0.0, 1.0);
        self
    }

    pub fn connect(&mut self) -> BTreeMap<String, Value> {
        let mut status = BTreeMap::new();
        self.last_errors.clear();

        for provider in &mut self.providers {
            let name = provider.name().to_string();
            match provider.connect() {
                Ok(()) => {
                    status.insert(name, provider.health());
                }
                Err(error) => {
                    self.last_errors.insert(name.clone(), error.to_string());
                    status.insert(
                        name,
                        json!({"available": false, "active": false, "error": error.to_string()}),
                    );
                }
            }
        }
        status
    }

    pub fn sample_all(&mut self, shots: u64) -> Vec<QuantumState> {
        let mut states = Vec::new();
        self.last_errors.clear();

        for provider in &mut self.providers {
            let name = provider.name().to_string();
            match provider.sample(shots).and_then(normalize_sample) {
                Ok(state) => states.push(state),
                Err(error) => {
                    self.last_errors.insert(name, error.to_string());
                }
            }
        }

        self.last_states = states.clone();
        states
    }

    pub fn control_packet(&mut self, shots: u64) -> ControlPacket {
        let states = self.sample_all(shots);
        ControlPacket {
            qbt_version: "1.0".to_string(),
            active_sources: states.len(),
            quantum_mix: blend_quantum_entropy(&states, self.fallback),
            states,
            provider_errors: self.last_errors.clone(),
        }
    }

    pub fn status(&self) -> Value {
        let providers: BTreeMap<String, Value> = self
            .providers
            .iter()
            .map(|provider| (provider.name().to_string(), provider.health()))
            .collect();
        json!({
            "qbt_version": "1.0",
            "providers": providers,
            "last_quantum_mix": blend_quantum_entropy(&self.last_states, self.fallback),
            "provider_errors": self.last_errors.clone(),
        })
    }

    pub fn close(&mut self) {
        for provider in &mut self.providers {
            let _ = provider.close();
        }
    }
}

pub const CONFIG_KEYS: &[&str] = &[
    "IBM_QUANTUM_TOKEN",
    "IQP_API_TOKEN",
    "IBM_QUANTUM_INSTANCE",
    "IBM_QUANTUM_BACKEND",
    "IBM_QUANTUM_API_BASE",
    "IBM_QUANTUM_API_VERSION",
    "IBM_QUANTUM_TIMEOUT_SECONDS",
    "IBM_QUANTUM_QASM",
    "AZURE_QUANTUM_BEARER_TOKEN",
    "AZURE_QUANTUM_ENDPOINT",
    "AZURE_SUBSCRIPTION_ID",
    "AZURE_QUANTUM_RESOURCE_GROUP",
    "AZURE_QUANTUM_WORKSPACE",
    "AZURE_QUANTUM_TARGET",
    "AZURE_QUANTUM_API_VERSION",
];

pub fn default_env_path() -> PathBuf {
    env::var_os("QBT_ENV_FILE")
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from(".env"))
}

fn parse_env_line(line: &str) -> Option<(String, String)> {
    let trimmed = line.trim();
    if trimmed.is_empty() || trimmed.starts_with('#') {
        return None;
    }
    let (key, raw) = trimmed.split_once('=')?;
    let key = key.trim();
    if key.is_empty() {
        return None;
    }
    let mut value = raw.trim().to_string();
    if value.len() >= 2 {
        let first = value.as_bytes()[0] as char;
        let last = value.as_bytes()[value.len() - 1] as char;
        if (first == '"' && last == '"') || (first == '\'' && last == '\'') {
            value = value[1..value.len() - 1].to_string();
        }
    }
    Some((key.to_string(), value))
}

pub fn load_env_file(path: Option<&Path>, override_existing: bool) -> Result<Option<PathBuf>> {
    let env_path = path.map(PathBuf::from).unwrap_or_else(default_env_path);
    if !env_path.exists() {
        return Ok(None);
    }

    for line in fs::read_to_string(&env_path)?.lines() {
        if let Some((key, value)) = parse_env_line(line) {
            if override_existing || env::var_os(&key).is_none() {
                env::set_var(key, value);
            }
        }
    }
    Ok(Some(env_path))
}

pub fn config_status() -> BTreeMap<String, String> {
    let _ = load_env_file(None, false);
    CONFIG_KEYS
        .iter()
        .map(|key| {
            let state = if env::var_os(key).is_some() {
                "configured"
            } else {
                "missing"
            };
            ((*key).to_string(), state.to_string())
        })
        .collect()
}

pub fn write_env_file(path: &Path, values: &BTreeMap<String, String>) -> Result<()> {
    let mut output =
        String::from("# QBT Rust local credentials/configuration. NEVER commit this file.\n");
    for key in CONFIG_KEYS {
        if let Some(value) = values.get(*key) {
            output.push_str(key);
            output.push('=');
            output.push_str(value.trim());
            output.push('\n');
        }
    }
    fs::write(path, output)?;
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        fs::set_permissions(path, fs::Permissions::from_mode(0o600))?;
    }
    Ok(())
}

pub mod providers {
    use std::collections::BTreeMap;
    use std::thread;
    use std::time::{Duration, Instant};

    use chrono::Utc;
    use rand::rngs::StdRng;
    use rand::{Rng, SeedableRng};
    use reqwest::blocking::Client;
    use serde_json::{json, Value};
    use uuid::Uuid;

    use super::{
        load_env_file, ExecutionMode, QbtError, Quality, QuantumProvider, QuantumSample, Result,
    };

    pub struct SimulatorProvider {
        rng: StdRng,
        backend: String,
        connected: bool,
    }

    impl SimulatorProvider {
        pub fn new(seed: u64) -> Self {
            Self {
                rng: StdRng::seed_from_u64(seed),
                backend: "rust-prng-control".to_string(),
                connected: false,
            }
        }
    }

    impl QuantumProvider for SimulatorProvider {
        fn name(&self) -> &str {
            "simulator"
        }

        fn connect(&mut self) -> Result<()> {
            self.connected = true;
            Ok(())
        }

        fn health(&self) -> Value {
            json!({
                "available": true,
                "active": self.connected,
                "provider": self.name(),
                "backend": self.backend,
                "execution_mode": "simulator",
            })
        }

        fn sample(&mut self, shots: u64) -> Result<QuantumSample> {
            if !self.connected {
                self.connect()?;
            }
            let mut counts = BTreeMap::from([("0".to_string(), 0_u64), ("1".to_string(), 0_u64)]);
            for _ in 0..shots {
                let bit = if self.rng.gen_bool(0.5) { "1" } else { "0" };
                if let Some(value) = counts.get_mut(bit) {
                    *value += 1;
                }
            }

            Ok(QuantumSample {
                provider: self.name().to_string(),
                backend: self.backend.clone(),
                mode: ExecutionMode::Simulator,
                counts,
                shots,
                job_id: Some(format!("sim-{}", Uuid::new_v4())),
                timestamp: Utc::now().to_rfc3339(),
                metadata: json!({"warning": "Classical PRNG control; not quantum hardware."}),
                quality: Quality {
                    quality_class: "classical-control".to_string(),
                    confidence: Some(1.0),
                },
            })
        }
    }

    pub struct IbmQuantumProvider {
        client: Client,
        api_key: Option<String>,
        instance_crn: Option<String>,
        backend: Option<String>,
        base_url: String,
        api_version: String,
        bearer_token: Option<String>,
        max_wait: Duration,
    }

    impl IbmQuantumProvider {
        pub fn from_env() -> Self {
            let _ = load_env_file(None, false);
            let api_key = env_value("IBM_QUANTUM_TOKEN").or_else(|| env_value("IQP_API_TOKEN"));
            let max_wait = env_value("IBM_QUANTUM_TIMEOUT_SECONDS")
                .and_then(|value| value.parse::<u64>().ok())
                .unwrap_or(300);

            Self {
                client: Client::new(),
                api_key,
                instance_crn: env_value("IBM_QUANTUM_INSTANCE"),
                backend: env_value("IBM_QUANTUM_BACKEND"),
                base_url: env_value("IBM_QUANTUM_API_BASE")
                    .unwrap_or_else(|| "https://quantum.cloud.ibm.com/api".to_string())
                    .trim_end_matches('/')
                    .to_string(),
                api_version: env_value("IBM_QUANTUM_API_VERSION")
                    .unwrap_or_else(|| "2026-04-15".to_string()),
                bearer_token: None,
                max_wait: Duration::from_secs(max_wait),
            }
        }

        pub fn new(api_key: impl Into<String>, instance_crn: impl Into<String>) -> Self {
            let mut provider = Self::from_env();
            provider.api_key = Some(api_key.into());
            provider.instance_crn = Some(instance_crn.into());
            provider
        }

        pub fn with_backend(mut self, backend: impl Into<String>) -> Self {
            self.backend = Some(backend.into());
            self
        }

        fn bearer(&self) -> Result<&str> {
            self.bearer_token.as_deref().ok_or_else(|| {
                QbtError::Config("IBM bearer token has not been initialized".to_string())
            })
        }

        fn crn(&self) -> Result<&str> {
            self.instance_crn.as_deref().ok_or_else(|| {
                QbtError::Config("IBM_QUANTUM_INSTANCE must contain the instance CRN".to_string())
            })
        }

        fn exchange_iam_token(&self) -> Result<String> {
            let api_key = self.api_key.as_deref().ok_or_else(|| {
                QbtError::Config("IBM_QUANTUM_TOKEN or IQP_API_TOKEN is required".to_string())
            })?;

            let response: Value = self
                .client
                .post("https://iam.cloud.ibm.com/identity/token")
                .form(&[
                    ("grant_type", "urn:ibm:params:oauth:grant-type:apikey"),
                    ("apikey", api_key),
                ])
                .send()?
                .error_for_status()?
                .json()?;

            response
                .get("access_token")
                .and_then(Value::as_str)
                .map(ToOwned::to_owned)
                .ok_or_else(|| {
                    QbtError::InvalidResult(
                        "IBM IAM response did not contain access_token".to_string(),
                    )
                })
        }

        fn get_json(&self, path: &str) -> Result<Value> {
            let response = self
                .client
                .get(format!("{}{}", self.base_url, path))
                .header("Accept", "application/json")
                .header("Authorization", format!("Bearer {}", self.bearer()?))
                .header("Service-CRN", self.crn()?)
                .header("IBM-API-Version", &self.api_version)
                .send()?
                .error_for_status()?;
            Ok(response.json()?)
        }

        fn choose_backend(&self) -> Result<String> {
            let body = self.get_json("/v1/backends")?;
            find_backend_name(&body).ok_or_else(|| {
                QbtError::InvalidResult(
                    "IBM backend list did not contain a backend name; set IBM_QUANTUM_BACKEND"
                        .to_string(),
                )
            })
        }

        fn submit_sampler(&self, shots: u64) -> Result<String> {
            let backend = self
                .backend
                .as_deref()
                .ok_or_else(|| QbtError::Config("IBM backend is not selected".to_string()))?;

            let qasm = env_value("IBM_QUANTUM_QASM").unwrap_or_else(|| {
                "OPENQASM 3.0; include \"stdgates.inc\"; bit[1] c; sx $0; c[0] = measure $0;"
                    .to_string()
            });

            let payload = json!({
                "program_id": "sampler",
                "backend": backend,
                "params": {
                    "pubs": [[qasm, Value::Null, shots]],
                    "options": {},
                    "version": 2
                }
            });

            let response: Value = self
                .client
                .post(format!("{}/v1/jobs", self.base_url))
                .header("Accept", "application/json")
                .header("Authorization", format!("Bearer {}", self.bearer()?))
                .header("Service-CRN", self.crn()?)
                .header("IBM-API-Version", &self.api_version)
                .json(&payload)
                .send()?
                .error_for_status()?
                .json()?;

            response
                .get("id")
                .and_then(Value::as_str)
                .map(ToOwned::to_owned)
                .ok_or_else(|| {
                    QbtError::InvalidResult("IBM job response did not contain id".to_string())
                })
        }

        fn wait_for_counts(&self, job_id: &str) -> Result<BTreeMap<String, u64>> {
            let started = Instant::now();
            loop {
                let details = self.get_json(&format!("/v1/jobs/{job_id}"))?;
                if let Some(status) = details
                    .get("state")
                    .and_then(|state| state.get("status"))
                    .and_then(Value::as_str)
                {
                    match status.to_ascii_lowercase().as_str() {
                        "completed" | "done" => break,
                        "failed" | "cancelled" | "canceled" => {
                            return Err(QbtError::Provider(format!(
                                "IBM job {job_id} ended with status {status}"
                            )));
                        }
                        _ => {}
                    }
                }

                if started.elapsed() >= self.max_wait {
                    return Err(QbtError::Timeout(format!(
                        "IBM job {job_id} did not complete within {} seconds",
                        self.max_wait.as_secs()
                    )));
                }
                thread::sleep(Duration::from_secs(2));
            }

            let results = self.get_json(&format!("/v1/jobs/{job_id}/results"))?;
            samples_to_counts(&results)
        }
    }

    impl QuantumProvider for IbmQuantumProvider {
        fn name(&self) -> &str {
            "ibm"
        }

        fn connect(&mut self) -> Result<()> {
            self.bearer_token = Some(self.exchange_iam_token()?);
            if self.instance_crn.is_none() {
                return Err(QbtError::Config(
                    "IBM_QUANTUM_INSTANCE must be the IBM Quantum instance CRN".to_string(),
                ));
            }
            if self.backend.is_none() {
                self.backend = Some(self.choose_backend()?);
            }
            Ok(())
        }

        fn health(&self) -> Value {
            json!({
                "available": self.bearer_token.is_some(),
                "active": self.bearer_token.is_some() && self.backend.is_some(),
                "provider": self.name(),
                "backend": self.backend.clone(),
                "execution_mode": "hardware",
                "api_version": self.api_version.clone(),
                "credential_source": if self.api_key.is_some() { "explicit/env" } else { "missing" },
                "instance_configured": self.instance_crn.is_some(),
            })
        }

        fn sample(&mut self, shots: u64) -> Result<QuantumSample> {
            if self.bearer_token.is_none() {
                self.connect()?;
            }
            let job_id = self.submit_sampler(shots)?;
            let counts = self.wait_for_counts(&job_id)?;
            let observed_shots = counts.values().copied().sum();

            Ok(QuantumSample {
                provider: self.name().to_string(),
                backend: self
                    .backend
                    .clone()
                    .unwrap_or_else(|| "unknown".to_string()),
                mode: ExecutionMode::Hardware,
                counts,
                shots: observed_shots,
                job_id: Some(job_id),
                timestamp: Utc::now().to_rfc3339(),
                metadata: json!({
                    "primitive": "sampler",
                    "primitive_version": 2,
                    "api_version": self.api_version.clone(),
                    "circuit": "1q-sx-measurement or IBM_QUANTUM_QASM override",
                    "provider_contract": "qbt-1.0",
                }),
                quality: Quality {
                    quality_class: "hardware".to_string(),
                    confidence: None,
                },
            })
        }
    }

    fn find_backend_name(value: &Value) -> Option<String> {
        if let Some(name) = value.get("name").and_then(Value::as_str) {
            return Some(name.to_string());
        }
        match value {
            Value::Array(items) => items.iter().find_map(find_backend_name),
            Value::Object(map) => map.values().find_map(find_backend_name),
            _ => None,
        }
    }

    fn samples_to_counts(results: &Value) -> Result<BTreeMap<String, u64>> {
        let samples = results
            .get("results")
            .and_then(Value::as_array)
            .and_then(|items| items.first())
            .and_then(|item| item.get("data"))
            .and_then(|data| data.get("c").or_else(|| data.get("meas")))
            .and_then(|register| register.get("samples"))
            .and_then(Value::as_array)
            .ok_or_else(|| {
                QbtError::InvalidResult(
                    "IBM Sampler result did not contain results[0].data.<register>.samples"
                        .to_string(),
                )
            })?;

        let mut counts = BTreeMap::new();
        for sample in samples {
            let encoded = sample.as_str().ok_or_else(|| {
                QbtError::InvalidResult("IBM sample was not a string".to_string())
            })?;
            let value = if let Some(raw_hex) = encoded.strip_prefix("0x") {
                u64::from_str_radix(raw_hex, 16).map_err(|_| {
                    QbtError::InvalidResult(format!("invalid IBM hex sample: {encoded}"))
                })?
            } else {
                encoded.parse::<u64>().map_err(|_| {
                    QbtError::InvalidResult(format!("invalid IBM sample: {encoded}"))
                })?
            };
            let bit = if value & 1 == 1 { "1" } else { "0" };
            *counts.entry(bit.to_string()).or_insert(0) += 1;
        }
        Ok(counts)
    }

    #[derive(Debug, Clone)]
    pub struct AzureRunResult {
        pub counts: BTreeMap<String, u64>,
        pub job_id: Option<String>,
        pub backend: String,
        pub metadata: Value,
        pub confidence: Option<f64>,
    }

    pub trait AzureRunner: Send {
        fn health(&self) -> Value;
        fn run(&mut self, shots: u64) -> Result<AzureRunResult>;
    }

    pub struct AzureQuantumProvider {
        runner: Box<dyn AzureRunner>,
    }

    impl AzureQuantumProvider {
        pub fn new(runner: Box<dyn AzureRunner>) -> Self {
            Self { runner }
        }
    }

    impl QuantumProvider for AzureQuantumProvider {
        fn name(&self) -> &str {
            "azure"
        }

        fn connect(&mut self) -> Result<()> {
            Ok(())
        }

        fn health(&self) -> Value {
            self.runner.health()
        }

        fn sample(&mut self, shots: u64) -> Result<QuantumSample> {
            let result = self.runner.run(shots)?;
            let observed_shots: u64 = result.counts.values().copied().sum();
            Ok(QuantumSample {
                provider: self.name().to_string(),
                backend: result.backend,
                mode: ExecutionMode::Hardware,
                counts: result.counts,
                shots: observed_shots,
                job_id: result.job_id,
                timestamp: Utc::now().to_rfc3339(),
                metadata: result.metadata,
                quality: Quality {
                    quality_class: "hardware".to_string(),
                    confidence: result.confidence,
                },
            })
        }
    }

    #[derive(Debug, Clone)]
    pub struct AzureRestClient {
        client: Client,
        pub endpoint: String,
        pub subscription_id: String,
        pub resource_group: String,
        pub workspace: String,
        pub bearer_token: String,
        pub api_version: String,
    }

    impl AzureRestClient {
        pub fn from_env() -> Result<Self> {
            Ok(Self {
                client: Client::new(),
                endpoint: required_env("AZURE_QUANTUM_ENDPOINT")?
                    .trim_end_matches('/')
                    .to_string(),
                subscription_id: required_env("AZURE_SUBSCRIPTION_ID")?,
                resource_group: required_env("AZURE_QUANTUM_RESOURCE_GROUP")?,
                workspace: required_env("AZURE_QUANTUM_WORKSPACE")?,
                bearer_token: required_env("AZURE_QUANTUM_BEARER_TOKEN")?,
                api_version: env_value("AZURE_QUANTUM_API_VERSION")
                    .unwrap_or_else(|| "2026-01-15-preview".to_string()),
            })
        }

        fn jobs_url(&self) -> String {
            format!(
                "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Quantum/workspaces/{}/jobs",
                self.endpoint, self.subscription_id, self.resource_group, self.workspace
            )
        }

        pub fn list_jobs(&self) -> Result<Value> {
            let response = self
                .client
                .get(self.jobs_url())
                .query(&[("api-version", self.api_version.as_str())])
                .bearer_auth(&self.bearer_token)
                .send()?
                .error_for_status()?;
            Ok(response.json()?)
        }

        pub fn get_job(&self, job_id: &str) -> Result<Value> {
            let response = self
                .client
                .get(format!("{}/{}", self.jobs_url(), job_id))
                .query(&[("api-version", self.api_version.as_str())])
                .bearer_auth(&self.bearer_token)
                .send()?
                .error_for_status()?;
            Ok(response.json()?)
        }

        pub fn create_job(&self, job_id: &str, body: &Value) -> Result<Value> {
            let response = self
                .client
                .put(format!("{}/{}", self.jobs_url(), job_id))
                .query(&[("api-version", self.api_version.as_str())])
                .bearer_auth(&self.bearer_token)
                .json(body)
                .send()?
                .error_for_status()?;
            Ok(response.json()?)
        }

        pub fn health_json(&self) -> Value {
            json!({
                "available": true,
                "active": true,
                "provider": "azure",
                "workspace": self.workspace.clone(),
                "endpoint": self.endpoint.clone(),
                "execution_mode": "hardware",
                "credential_source": "bearer-token",
            })
        }
    }

    fn env_value(key: &str) -> Option<String> {
        std::env::var(key)
            .ok()
            .filter(|value| !value.trim().is_empty())
    }

    fn required_env(key: &str) -> Result<String> {
        env_value(key).ok_or_else(|| QbtError::Config(format!("{key} is not configured")))
    }

    #[cfg(test)]
    mod tests {
        use super::*;

        #[test]
        fn parses_ibm_rest_samples() {
            let payload = json!({
                "results": [{"data": {"c": {"samples": ["0x0", "0x1", "0x1"]}}}]
            });
            let counts = samples_to_counts(&payload).expect("valid samples");
            assert_eq!(counts["0"], 1);
            assert_eq!(counts["1"], 2);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn entropy_extremes() {
        let deterministic = BTreeMap::from([("0".to_string(), 100)]);
        let balanced = BTreeMap::from([("0".to_string(), 50), ("1".to_string(), 50)]);
        assert_eq!(entropy_from_counts(&deterministic), 0.0);
        assert!((entropy_from_counts(&balanced) - 1.0).abs() < f64::EPSILON);
    }
}
