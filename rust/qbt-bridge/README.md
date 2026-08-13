# qbt-bridge for Rust

Native Rust implementation of the Quantum Bridge Transformer core.

This is **not** a Python subprocess wrapper. Rust implements its own provider trait, normalized state model, SHA-256 provenance, fail-soft bridge, simulator, IBM Quantum REST flow, Azure Quantum REST helpers, CLI, tests, and examples.

```text
quantum provider
    -> QuantumSample
    -> normalized QuantumState
    -> SHA-256 provenance
    -> bounded ControlPacket
    -> your Rust application / model / controller
```

## Run

```bash
cd rust/qbt-bridge
cargo test
cargo run --bin qbt-rs -- sample --provider simulator --shots 1024
```

## IBM hardware from Rust

```bash
export IBM_QUANTUM_TOKEN="your IBM API key"
export IBM_QUANTUM_INSTANCE="your IBM Quantum instance CRN"
export IBM_QUANTUM_BACKEND="backend-name"

cargo run --bin qbt-rs -- status --provider ibm
cargo run --bin qbt-rs -- sample --provider ibm --shots 1024
```

The IBM provider exchanges the user's API key for a short-lived IBM Cloud IAM bearer token, submits a Sampler V2 REST job, polls job state, retrieves the samples, converts them to counts, and produces the same normalized QBT packet used by the simulator.

## Azure Quantum from Rust

Azure Quantum has multiple provider-specific input/output formats. The crate therefore exposes both:

- `AzureRestClient` for the Azure Quantum data-plane job API.
- `AzureQuantumProvider` + `AzureRunner` for target-specific executions that return counts into QBT core.

See the repository-root [`RUST_USERS.md`](../../RUST_USERS.md) for full integration instructions.
