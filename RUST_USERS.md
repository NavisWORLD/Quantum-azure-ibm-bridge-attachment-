# Rust Users — Native QBT Integration

The repository now includes a **native Rust implementation** of the Quantum Bridge Transformer under `rust/qbt-bridge/`.

It is not a Python subprocess wrapper. The Rust crate implements its own:

- provider trait
- typed quantum sample/state contracts
- Shannon-entropy normalization
- bounded multi-provider mixing
- SHA-256 provenance digests
- fail-soft provider isolation
- seeded simulator/classical control source
- IBM Quantum REST authentication and Sampler V2 job flow
- Azure Quantum data-plane REST helpers
- Azure target-runner integration trait
- local `.env` loading and masked configuration status
- CLI
- tests and examples

## Quick start

```bash
cd rust/qbt-bridge
cargo test
cargo run --bin qbt-rs -- sample --provider simulator --shots 1024
```

The simulator is explicitly labeled `simulator`; it is a classical control, not quantum hardware.

## Add QBT to another Rust project

The simplest development setup is a path dependency:

```toml
[dependencies]
qbt-bridge = { path = "../Quantum-azure-ibm-bridge-attachment-/rust/qbt-bridge" }
```

Then:

```rust
use qbt_bridge::providers::SimulatorProvider;
use qbt_bridge::QuantumBridge;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut bridge = QuantumBridge::new(vec![
        Box::new(SimulatorProvider::new(7)),
    ]);

    bridge.connect();
    let packet = bridge.control_packet(2048);

    println!("mix={}", packet.quantum_mix);
    println!("digest={}", packet.states[0].result_digest);
    Ok(())
}
```

The JSON shape mirrors the Python implementation so Rust and Python services can exchange QBT packets at a language-neutral boundary.

## Core provider contract

Any provider can implement:

```rust
use qbt_bridge::{QuantumProvider, QuantumSample, Result};

pub struct MyProvider;

impl QuantumProvider for MyProvider {
    fn name(&self) -> &str {
        "my-provider"
    }

    fn connect(&mut self) -> Result<()> {
        Ok(())
    }

    fn health(&self) -> serde_json::Value {
        serde_json::json!({"available": true, "active": true})
    }

    fn sample(&mut self, shots: u64) -> Result<QuantumSample> {
        todo!("return provider counts and provenance")
    }
}
```

The host application therefore consumes `QuantumState` rather than IBM/Azure-specific SDK objects.

# IBM Quantum from Rust

The Rust IBM provider uses IBM Quantum's language-neutral REST API.

Configure:

```dotenv
IBM_QUANTUM_TOKEN=
IBM_QUANTUM_INSTANCE=
IBM_QUANTUM_BACKEND=
```

`IBM_QUANTUM_INSTANCE` must be the IBM Quantum Compute instance **CRN**.

Run:

```bash
cd rust/qbt-bridge
cargo run --bin qbt-rs -- status --provider ibm
cargo run --bin qbt-rs -- sample --provider ibm --shots 1024
```

The execution path is:

```text
IBM API key
   ↓
IBM Cloud IAM exchange
   ↓
short-lived bearer token
   ↓
Sampler V2 REST job
   ↓
poll job state
   ↓
GET job results
   ↓
hex samples -> counts
   ↓
QBT normalization + provenance
```

The built-in single-qubit sample uses a physical-qubit `sx` plus measurement circuit. For a specific backend or advanced experiment, provide an ISA/pre-transpiled OpenQASM 3 program through:

```dotenv
IBM_QUANTUM_QASM=OPENQASM 3.0; ...
```

Optional IBM settings:

```dotenv
IBM_QUANTUM_API_BASE=https://quantum.cloud.ibm.com/api
IBM_QUANTUM_API_VERSION=2026-04-15
IBM_QUANTUM_TIMEOUT_SECONDS=300
```

For a region-specific IBM endpoint, set `IBM_QUANTUM_API_BASE` to the endpoint documented for your instance.

# Azure Quantum from Rust

Azure Quantum targets can require different job payloads, input formats, storage objects, and result schemas. The Rust implementation does not falsely pretend that one target-specific payload works for every provider.

It gives Rust users two layers:

1. `AzureRestClient` — low-level Azure Quantum data-plane job API.
2. `AzureQuantumProvider` + `AzureRunner` — a target-specific execution adapter that returns normalized counts into QBT.

## Azure REST client

Configure:

```dotenv
AZURE_QUANTUM_BEARER_TOKEN=
AZURE_QUANTUM_ENDPOINT=
AZURE_SUBSCRIPTION_ID=
AZURE_QUANTUM_RESOURCE_GROUP=
AZURE_QUANTUM_WORKSPACE=
AZURE_QUANTUM_TARGET=
```

Then:

```rust
use qbt_bridge::providers::AzureRestClient;

fn main() -> qbt_bridge::Result<()> {
    let azure = AzureRestClient::from_env()?;
    let jobs = azure.list_jobs()?;
    println!("{}", serde_json::to_string_pretty(&jobs)?);
    Ok(())
}
```

`AzureRestClient` implements:

- `list_jobs()`
- `get_job(job_id)`
- `create_job(job_id, json_body)`

The bearer token should come from your organization's Microsoft Entra, managed-identity, CLI, or secret-broker flow. Never commit it.

## Target-specific Azure runner

```rust
use std::collections::BTreeMap;

use qbt_bridge::providers::{AzureRunResult, AzureRunner};
use qbt_bridge::Result;
use serde_json::json;

struct MyAzureRunner;

impl AzureRunner for MyAzureRunner {
    fn health(&self) -> serde_json::Value {
        json!({"available": true, "active": true, "target": "my-target"})
    }

    fn run(&mut self, _shots: u64) -> Result<AzureRunResult> {
        Ok(AzureRunResult {
            counts: BTreeMap::from([
                ("0".to_string(), 510),
                ("1".to_string(), 514),
            ]),
            job_id: Some("provider-job-id".to_string()),
            backend: "my-target".to_string(),
            metadata: json!({"source": "azure-quantum"}),
            confidence: None,
        })
    }
}
```

Attach it:

```rust
use qbt_bridge::providers::AzureQuantumProvider;
use qbt_bridge::QuantumBridge;

let provider = AzureQuantumProvider::new(Box::new(MyAzureRunner));
let mut bridge = QuantumBridge::new(vec![Box::new(provider)]);
let packet = bridge.control_packet(1024);
```

# Rust CLI

```text
qbt-rs doctor
qbt-rs configure
qbt-rs status --provider simulator
qbt-rs sample --provider simulator --shots 1024
qbt-rs status --provider ibm
qbt-rs sample --provider ibm --shots 1024
```

`doctor` reports only whether each setting is configured or missing. It does not print token values.

# Data-model parity

Both Python and Rust use the same conceptual contract:

```text
QuantumSample
  provider
  backend
  execution mode
  counts
  shots
  job id
  timestamp
  metadata
  quality
      ↓
normalize
      ↓
QuantumState
  qbt_version
  entropy [0,1]
  normalized vector
  SHA-256 result digest
  provenance
```

# Production checklist

- Keep provider credentials outside Git.
- Gate real QPU calls behind authorization and spending policy.
- Preserve hardware/simulator/archive/fallback labels.
- Persist QBT packets beside downstream decisions when auditability matters.
- Replay archived packets for deterministic regression tests.
- Compare real hardware against matched classical controls before claiming performance advantage.

# Scientific boundary

The Rust port preserves the same claim discipline as the Python implementation:

> A real quantum job can establish that a quantum-derived signal entered the pipeline. It does not by itself establish that the signal improved the downstream AI.

That remains an experimental question.
