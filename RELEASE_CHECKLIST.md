# QBT 0.3.0 Release Readiness Checklist

This checklist defines what "ready" means for the Quantum Bridge Transformer universal-compatibility release.

## Repository gates

- [x] Apache-2.0 `LICENSE`
- [x] `NOTICE`
- [x] `CITATION.cff`
- [x] root README with Python, Rust, HTTP/JSON, and C ABI entry points
- [x] Python package metadata
- [x] root Cargo workspace
- [x] native Rust SDK metadata
- [x] native C ABI crate metadata
- [x] `LANGUAGE_COMPATIBILITY.md`
- [x] language-binding overview
- [x] API-key / credential setup documentation
- [x] security policy
- [x] contribution guide and issue templates
- [x] teacher manual
- [x] architecture and integration manuals
- [x] proof-of-concept evidence ledger
- [x] publication-style manuscript
- [x] launch/demo materials

## Canonical protocol gates

- [x] language-neutral QBT protocol document
- [x] `QuantumState` JSON Schema
- [x] `ControlPacket` JSON Schema
- [x] OpenAPI 3.1 sidecar contract
- [x] execution-mode enum is consistent across implementations
- [x] four-element normalized vector contract is documented
- [x] SHA-256 provenance contract is preserved
- [x] provider errors have a cross-language representation

## Python gates

- [x] installable package
- [x] simulator/control provider
- [x] IBM Quantum adapter
- [x] Azure Quantum adapter
- [x] fail-soft bridge behavior
- [x] normalized `QuantumState`
- [x] `provider_errors` in `ControlPacket`
- [x] SHA-256 provenance
- [x] prompt-safe integration
- [x] optional PyTorch conditioner
- [x] BYOK `.env` loading
- [x] hidden secret entry in configuration flow
- [x] masked credential status
- [x] `qbt serve` universal sidecar entry point
- [x] sidecar endpoint/security unit tests
- [x] protocol/schema tests
- [x] Ruff linting configured
- [ ] final CI green on Python 3.10, 3.11, and 3.12

## Rust SDK gates

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
- [ ] final `cargo fmt --all -- --check` green
- [ ] final `cargo test --workspace --all-targets` green
- [ ] final `cargo clippy --workspace --all-targets -- -D warnings` green
- [ ] final Rust workspace tests green on Windows
- [ ] final Rust workspace tests green on macOS

## Universal HTTP/JSON gates

- [x] loopback-only default bind
- [x] non-loopback bind requires bearer token
- [x] explicit opt-in browser CORS
- [x] request-body limit
- [x] bounded shot-count input
- [x] no raw provider credentials in HTTP responses
- [x] live IBM/Azure sidecar execution disabled by default
- [x] explicit `--allow-live-providers` / `QBT_ALLOW_LIVE_PROVIDERS=1` opt-in
- [x] live-provider safety behavior covered by tests
- [x] `GET /health`
- [x] `GET /v1/status`
- [x] `POST /v1/sample`
- [x] `POST /v1/normalize`
- [ ] final sidecar smoke green on Linux
- [ ] final sidecar smoke green on Windows
- [ ] final sidecar smoke green on macOS

## Native C ABI gates

- [x] `qbt-ffi` Rust crate
- [x] `cdylib` output
- [x] `staticlib` output
- [x] stable UTF-8 JSON exchange boundary
- [x] `qbt_version`
- [x] `qbt_simulator_packet`
- [x] `qbt_normalize_counts_json`
- [x] `qbt_free_string`
- [x] portable `qbt.h`
- [x] C++ RAII wrapper `qbt.hpp`
- [x] Rust-side FFI unit tests
- [ ] final linked C executable smoke green
- [ ] final linked C++ executable smoke green

## Language adapter gates

Implementation is present for every checked item. The final CI boxes remain open until the adapter executes against a live local QBT sidecar on the release commit.

- [x] JavaScript client implemented
- [x] TypeScript declarations implemented
- [x] Go typed client implemented
- [x] Java/JVM client implemented
- [x] Kotlin interoperability documented through the JVM adapter
- [x] C#/.NET client implemented
- [x] Swift client implemented
- [x] PHP client implemented with numeric-bitstring count-map preservation
- [x] Ruby client implemented
- [x] Perl client implemented
- [x] shell/curl client implemented
- [x] PowerShell client implemented
- [ ] JavaScript end-to-end smoke green
- [ ] TypeScript declaration check green
- [ ] Go end-to-end smoke green
- [ ] Java/JVM end-to-end smoke green
- [ ] C#/.NET end-to-end smoke green
- [ ] Swift end-to-end smoke green
- [ ] PHP end-to-end smoke green
- [ ] Ruby end-to-end smoke green
- [ ] Perl end-to-end smoke green
- [ ] shell/curl end-to-end smoke green
- [ ] PowerShell end-to-end smoke green

## Long-tail language compatibility

These ecosystems do not need duplicated provider logic. They use one of the two universal contracts.

- [x] C/C++ through native ABI
- [x] Objective-C through C ABI
- [x] Zig/Nim/D through C ABI
- [x] Fortran through `ISO_C_BINDING`
- [x] Julia through HTTP/JSON or `ccall`
- [x] R through HTTP/JSON
- [x] Dart/Flutter through HTTP/JSON
- [x] Lua through HTTP/JSON or FFI
- [x] Haskell through HTTP/JSON or FFI
- [x] Scala/Clojure through JVM adapter/HTTP
- [x] F#/VB.NET through .NET HTTP/PInvoke surface
- [x] Elixir/Erlang through HTTP/JSON
- [x] OCaml through HTTP/JSON or C ABI
- [x] MATLAB/Octave through HTTP/JSON or native-library loading
- [x] any other runtime able to speak HTTP/JSON or call a C-compatible library

## Live-provider acceptance test

Public CI deliberately contains **no IBM or Azure credentials**. A live hardware/workspace path is accepted for a specific user/account only after that user supplies their own credentials and completes the appropriate smoke test.

The HTTP sidecar intentionally refuses live IBM/Azure sampling unless the operator explicitly enables it. Direct Python/Rust CLI provider commands remain explicit operator actions and keep their existing behavior.

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

A successful live acceptance record should retain provider/backend, job ID, shots, execution mode, and result digest. Never publish an API key.

### Azure

1. Configure the user's own Azure Quantum workspace / target and authentication.
2. Run the documented Azure workspace or target-specific runner example.
3. Confirm the returned record is labeled with the correct execution mode and target.
4. Retain job/result provenance without storing credentials in the control packet.

## Claim boundary

Passing this checklist establishes that the software package is installable, tested, linted, documented, cross-language compatible through defined protocols, provider-ready, and capable of producing normalized/auditable control state.

It does **not** claim that every programming language has a bespoke provider SDK, that every third-party provider account is provisioned, that QPU queues are always available, or that quantum conditioning improves ML accuracy. HTTP/JSON and the C ABI are the universal compatibility contracts for languages without a dedicated reference adapter.

## Current release status

**QBT v0.3.0 becomes release-ready when every pending automated gate above is green on the exact final commit.**
