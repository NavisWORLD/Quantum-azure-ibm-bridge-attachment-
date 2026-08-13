//! Stable C ABI for the native QBT Rust core.
//!
//! The ABI exchanges owned UTF-8 JSON strings so C-compatible languages do
//! not need to mirror Rust layouts. Returned strings must be released with
//! `qbt_free_string`.

use std::collections::BTreeMap;
use std::ffi::{CStr, CString};
use std::os::raw::c_char;
use std::ptr;

use chrono::Utc;
use qbt_bridge::providers::SimulatorProvider;
use qbt_bridge::{
    normalize_sample, ExecutionMode, Quality, QuantumBridge, QuantumSample,
};
use serde::Deserialize;
use serde_json::{json, Value};

static VERSION: &[u8] = b"1.0\0";

#[derive(Debug, Deserialize)]
struct NormalizeRequest {
    provider: Option<String>,
    backend: Option<String>,
    mode: Option<ExecutionMode>,
    counts: BTreeMap<String, u64>,
    shots: Option<u64>,
    job_id: Option<String>,
    timestamp: Option<String>,
    metadata: Option<Value>,
    quality_class: Option<String>,
    confidence: Option<f64>,
}

fn owned_json(value: &impl serde::Serialize) -> *mut c_char {
    let serialized = match serde_json::to_string(value) {
        Ok(value) => value,
        Err(error) => format!("{{\"error\":\"serialization failure: {error}\"}}"),
    };
    match CString::new(serialized) {
        Ok(value) => value.into_raw(),
        Err(_) => ptr::null_mut(),
    }
}

fn error_json(message: impl ToString) -> *mut c_char {
    owned_json(&json!({"error": message.to_string()}))
}

/// Return the QBT wire-protocol version as a static NUL-terminated string.
///
/// The returned pointer is static storage and must not be freed.
#[no_mangle]
pub extern "C" fn qbt_version() -> *const c_char {
    VERSION.as_ptr().cast()
}

/// Produce a simulator `ControlPacket` as an owned UTF-8 JSON string.
///
/// The returned pointer must be released with `qbt_free_string`.
#[no_mangle]
pub extern "C" fn qbt_simulator_packet(seed: u64, shots: u64) -> *mut c_char {
    if shots == 0 {
        return error_json("shots must be greater than zero");
    }
    let mut bridge = QuantumBridge::new(vec![Box::new(SimulatorProvider::new(seed))]);
    bridge.connect();
    owned_json(&bridge.control_packet(shots))
}

/// Normalize an external counts payload into a `QuantumState` JSON object.
///
/// # Safety
///
/// `request_json` must point to a valid NUL-terminated UTF-8 C string for the
/// duration of this call. The returned pointer must be released with
/// `qbt_free_string`.
#[no_mangle]
pub unsafe extern "C" fn qbt_normalize_counts_json(request_json: *const c_char) -> *mut c_char {
    if request_json.is_null() {
        return error_json("request_json must not be null");
    }

    let text = match unsafe { CStr::from_ptr(request_json) }.to_str() {
        Ok(value) => value,
        Err(error) => return error_json(format!("request is not UTF-8: {error}")),
    };
    let request: NormalizeRequest = match serde_json::from_str(text) {
        Ok(value) => value,
        Err(error) => return error_json(format!("invalid request JSON: {error}")),
    };
    if request.counts.is_empty() {
        return error_json("counts must not be empty");
    }
    let shots = request
        .shots
        .unwrap_or_else(|| request.counts.values().copied().sum());
    if shots == 0 {
        return error_json("shots must be greater than zero");
    }

    let sample = QuantumSample {
        provider: request.provider.unwrap_or_else(|| "external".to_string()),
        backend: request.backend.unwrap_or_else(|| "external".to_string()),
        mode: request.mode.unwrap_or(ExecutionMode::Simulator),
        counts: request.counts,
        shots,
        job_id: request.job_id,
        timestamp: request.timestamp.unwrap_or_else(|| Utc::now().to_rfc3339()),
        metadata: request.metadata.unwrap_or_else(|| json!({})),
        quality: Quality {
            quality_class: request
                .quality_class
                .unwrap_or_else(|| "ffi-external".to_string()),
            confidence: request.confidence,
        },
    };

    match normalize_sample(sample) {
        Ok(state) => owned_json(&state),
        Err(error) => error_json(error),
    }
}

/// Release a string returned by a QBT FFI function.
///
/// # Safety
///
/// `value` must be null or a pointer previously returned by a QBT FFI
/// function that transfers ownership to the caller. Do not free `qbt_version`.
#[no_mangle]
pub unsafe extern "C" fn qbt_free_string(value: *mut c_char) {
    if !value.is_null() {
        drop(unsafe { CString::from_raw(value) });
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn simulator_packet_round_trips_through_c_string() {
        let raw = qbt_simulator_packet(7, 128);
        assert!(!raw.is_null());
        let text = unsafe { CStr::from_ptr(raw) }.to_str().unwrap();
        let value: Value = serde_json::from_str(text).unwrap();
        assert_eq!(value["active_sources"], 1);
        assert!(value["quantum_mix"].as_f64().unwrap() >= 0.0);
        unsafe { qbt_free_string(raw) };
    }

    #[test]
    fn normalize_counts_returns_bounded_state() {
        let request = CString::new(
            r#"{"provider":"ffi","backend":"test","mode":"simulator","counts":{"0":64,"1":64},"shots":128}"#,
        )
        .unwrap();
        let raw = unsafe { qbt_normalize_counts_json(request.as_ptr()) };
        assert!(!raw.is_null());
        let text = unsafe { CStr::from_ptr(raw) }.to_str().unwrap();
        let value: Value = serde_json::from_str(text).unwrap();
        assert_eq!(value["entropy"].as_f64().unwrap(), 1.0);
        assert_eq!(value["normalized_vector"].as_array().unwrap().len(), 4);
        unsafe { qbt_free_string(raw) };
    }
}
