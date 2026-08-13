# QBT Release Readiness Checklist

This checklist defines what "ready" means for the Quantum Bridge Transformer repository.

## Repository gates

- [x] Apache-2.0 `LICENSE`
- [x] `NOTICE`
- [x] `CITATION.cff`
- [x] root README with Python and Rust entry points
- [x] Python package metadata
- [x] root Cargo workspace
- [x] native Rust crate metadata
- [x] API-key / credential setup documentation
- [x] security policy
- [x] contribution guide and issue templates
- [x] teacher manual
- [x] architecture and integration manuals
- [x] proof-of-concept evidence ledger
- [x] publication-style manuscript
- [x] launch/demo materials

## Python gates

- [x] installable package
- [x] simulator/control provider
- [x] IBM Quantum adapter
- [x] Azure Quantum adapter
- [x] fail-soft bridge behavior
- [x] normalized `QuantumState`
- [x] SHA-256 provenance
- [x] prompt-safe integration
- [x] optional PyTorch conditioner
- [x] BYOK `.env` loading
- [x] hidden secret entry in configuration flow
- [x] masked credential status
- [x] automated tests
- [x] Ruff linting
- [x] CI on Python 3.10, 3.11, and 3.12

## Rust gates

- [x] native `qbt-bridge` crate
- [x] `QuantumProvider` trait
- [x] fail-soft `QuantumBridge`
- [x] `QuantumSample`, `QuantumState`, and `ControlPacket`
- [x] bounded entropy normalization/blending
- [x] SHA-256 provenance
- [x] simulator/control provider
- [x] native IBM REST path
- [x] IBM IAM token exchange / job polling / result normalization path
- [x] Azure Quantum REST primitives
- [x] Azure target-specific runner abstraction
- [x] `.env` configuration
- [x] hidden terminal input for secrets
- [x] masked `doctor` output
- [x] `qbt-rs` CLI
- [x] Rust examples
- [x] Rust integration tests
- [x] `cargo fmt --check`
- [x] `cargo test --all-targets`
- [x] `cargo clippy --all-targets -- -D warnings`

## Live-provider acceptance test

CI deliberately contains **no IBM or Azure credentials**. A live hardware/workspace path is accepted for a specific user/account only after that user supplies their own credentials and completes the appropriate smoke test.

### IBM

Python:

```bash
qbt doctor
qbt status --provider ibm
qbt sample --provider ibm --shots 128
```

Rust:

```bash
cargo run -p qbt-bridge --bin qbt-rs -- doctor
cargo run -p qbt-bridge --bin qbt-rs -- status --provider ibm
cargo run -p qbt-bridge --bin qbt-rs -- sample --provider ibm --shots 128
```

A successful live acceptance record should retain the returned provider/backend, job ID, shots, execution mode, and result digest. Never publish an API key.

### Azure

1. Configure the user's own Azure Quantum workspace / target and authentication.
2. Run the documented Azure workspace or target-specific runner example.
3. Confirm the returned record is labeled with the correct execution mode and target.
4. Retain the job/result provenance without storing credentials in the control packet.

## Claim boundary

Passing this checklist establishes that the software package is installable, tested, linted, documented, provider-ready, and capable of producing normalized/auditable control state.

It does **not** claim that every third-party provider account is provisioned, that QPU queues are always available, or that quantum conditioning improves ML accuracy. Those are account/runtime/experimental questions and must be verified independently.

## Current release status

**QBT v0.2.0 is release-ready once the green CI run corresponds to the final commit being merged.**
