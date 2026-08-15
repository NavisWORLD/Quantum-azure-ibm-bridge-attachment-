# Quantum Bridge Transformer (QBT)

[![CI](https://github.com/NavisWORLD/Quantum-azure-ibm-bridge-attachment-/actions/workflows/ci.yml/badge.svg)](https://github.com/NavisWORLD/Quantum-azure-ibm-bridge-attachment-/actions/workflows/ci.yml)
![QBT](https://img.shields.io/badge/QBT-0.4.0-blueviolet)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Rust](https://img.shields.io/badge/Rust-native-orange)
![C ABI](https://img.shields.io/badge/C%20ABI-FFI-informational)
![License](https://img.shields.io/badge/license-restricted%20source-critical)
![IBM Quantum](https://img.shields.io/badge/IBM-Quantum-6929C4)
![Azure Quantum](https://img.shields.io/badge/Azure-Quantum-0078D4)

> **Bring your own quantum account. Keep your own AI stack.**

QBT is a provider-neutral quantum-to-classical integration layer. It converts IBM Quantum, Azure Quantum, simulator, archive, or external measurement results into a bounded, auditable `QuantumState` / `ControlPacket` that ordinary AI systems, agents, simulations, games, robotics, research software, and control systems can consume.

## Current rights boundary

Current and future Cory-owned original material expressly distributed under the repository's current `LICENSE` is **not offered for general commercial reuse, redistribution, modification, derivative-work creation, or incorporation into other products without separate written permission**. Historical copies previously distributed under Apache-2.0 retain the rights validly granted to those copies. See `LICENSE`, `LICENSE_HISTORY.md`, and `COMMERCIAL_RIGHTS.md`.

Third-party dependencies and provider SDKs remain governed by their own licenses and terms.

QBT 0.4.0 ships four compatibility surfaces:

1. **Native Python SDK**
2. **Native Rust SDK**
3. **Universal JSON/HTTP sidecar**
4. **Native Rust-built C ABI** for FFI-capable languages

This gives QBT practical interoperability across Python, Rust, C, C++, JavaScript, TypeScript, Go, Java, Kotlin, C#, F#, Swift, Objective-C, PHP, Ruby, Perl, PowerShell, shell, Zig, Nim, D, Fortran, Julia, R, Dart, Lua, Haskell, Scala, Clojure, Elixir/Erlang, OCaml, MATLAB/Octave, and other environments that can call HTTP/JSON or a C-compatible library.

See **[`LANGUAGE_COMPATIBILITY.md`](LANGUAGE_COMPATIBILITY.md)** for the complete compatibility matrix.

QBT does **not** claim that a classical transformer suddenly executes on a QPU. It provides a disciplined, testable bridge between quantum-derived measurements and conventional software.

```text
 IBM Quantum ──┐
 Azure Quantum ┤
 Simulator ────┼────> provider adapters / external counts
 Archive ──────┤                    │
 Other source ─┘                    ▼
                              QuantumSample
                                    │
                     normalization + provenance
                                    │
                                    ▼
                              QuantumState
                                    │
                         bounded ControlPacket
                                    │
             ┌──────────────────────┼──────────────────────┐
             ▼                      ▼                      ▼
       Python / Rust           HTTP / JSON              C ABI
             │                      │                      │
             └────────────── your AI / app / system ─────┘
```

## Why engineers use it

- **Bring your own account**: no personal IBM/Azure credentials are included.
- **Provider-neutral contract**: downstream systems consume QBT state, not vendor SDK objects.
- **Native Python + Rust**: use QBT directly in either ecosystem.
- **Universal sidecar**: any HTTP/JSON-capable language can call the same tested core.
- **C ABI**: embed QBT from C-compatible FFI ecosystems without Python.
- **Safe live-provider boundary**: HTTP-triggered IBM/Azure jobs are disabled until explicitly enabled by the operator.
- **Auditable provenance**: provider, backend, job ID, shot count, timestamp, metadata, and SHA-256 digest.
- **Bounded influence**: normalized control values stay in `[0, 1]`.
- **Fail-soft behavior**: provider failures are reported without requiring the host AI process to crash.
- **Cross-platform**: compatibility CI covers Linux, Windows, and macOS paths.
- **Scientifically testable**: real hardware, simulator, classical random, fixed, and disabled controls remain separate.
- **Teachability**: architecture docs, teacher manual, labs, proof ledger, paper, and demo material are included.

# 1. Python quick start

```bash
git clone https://github.com/NavisWORLD/Quantum-azure-ibm-bridge-attachment-.git
cd Quantum-azure-ibm-bridge-attachment-
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
qbt sample --provider simulator --shots 1024
pytest
```

The default simulator is deliberately labeled as a classical control.

Python project integration:

```python
from qbt_bridge import QuantumBridge
from qbt_bridge.providers import SimulatorProvider

bridge = QuantumBridge([SimulatorProvider(seed=7)])
bridge.connect()
packet = bridge.control_packet(shots=2048)
print(packet["quantum_mix"])
```

# 2. Rust quick start

The repository root is a Cargo workspace:

```bash
cargo test --workspace --all-targets
cargo run -p qbt-bridge --bin qbt-rs -- sample --provider simulator --shots 1024
```

Use it from another Rust project:

```toml
[dependencies]
qbt-bridge = { path = "../Quantum-azure-ibm-bridge-attachment-/rust/qbt-bridge" }
```

```rust
use qbt_bridge::providers::SimulatorProvider;
use qbt_bridge::QuantumBridge;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut bridge = QuantumBridge::new(vec![Box::new(SimulatorProvider::new(7))]);
    bridge.connect();
    let packet = bridge.control_packet(2048);
    println!("mix={}", packet.quantum_mix);
    Ok(())
}
```

See **[`RUST_USERS.md`](RUST_USERS.md)** for IBM REST, Azure REST/runner integration, custom providers, credentials, and production guidance.

# 3. Universal HTTP/JSON

Start the safe local sidecar:

```bash
qbt serve --host 127.0.0.1 --port 8766
```

By default, the sidecar allows simulator sampling and normalization but **refuses HTTP-triggered live IBM/Azure job submission**. When an operator intentionally wants the sidecar to submit live provider work, enable it explicitly:

```bash
qbt serve --host 127.0.0.1 --port 8766 --allow-live-providers
```

or set:

```dotenv
QBT_ALLOW_LIVE_PROVIDERS=1
```

Endpoints:

```text
GET  /health
GET  /v1/status?provider=simulator|ibm|azure
POST /v1/sample
POST /v1/normalize
```

`GET /health` reports `live_provider_execution` so clients can see the execution policy without exposing credentials.

Example:

```bash
curl -s -H 'Content-Type: application/json' \
  -d '{"provider":"simulator","shots":1024,"seed":42}' \
  http://127.0.0.1:8766/v1/sample
```

External measurement normalization:

```bash
curl -s -H 'Content-Type: application/json' \
  -d '{"provider":"external","backend":"my-backend","mode":"hardware","counts":{"0":512,"1":512},"shots":1024}' \
  http://127.0.0.1:8766/v1/normalize
```

Security defaults:

- loopback only by default
- non-loopback binds require `QBT_SIDECAR_TOKEN`
- live IBM/Azure HTTP execution disabled by default
- live execution requires explicit operator opt-in
- raw provider credentials are never returned
- request bodies are size-limited
- shot requests are bounded
- browser CORS is disabled unless `QBT_ALLOW_ORIGIN` is explicitly configured

Canonical protocol files:

- `spec/qbt-state.schema.json`
- `spec/qbt-control-packet.schema.json`
- `spec/qbt-api.openapi.yaml`
- `spec/PROTOCOL.md`

Reference HTTP clients live under `bindings/`.

# 4. Native C ABI

Build the Rust FFI library:

```bash
cargo build -p qbt-ffi --release
```

Headers:

```text
rust/qbt-ffi/include/qbt.h
rust/qbt-ffi/include/qbt.hpp
```

Core exports:

```c
const char *qbt_version(void);
char *qbt_simulator_packet(uint64_t seed, uint64_t shots);
char *qbt_normalize_counts_json(const char *request_json);
void qbt_free_string(char *value);
```

Returned owned JSON strings are released with `qbt_free_string`. The protocol version pointer is static and must not be freed.

This ABI is directly usable from C/C++ and can be bound from Objective-C, Zig, Nim, D, Fortran `ISO_C_BINDING`, Julia `ccall`, Swift, .NET P/Invoke, JVM FFI/JNA/JNI/Panama, and other C-FFI ecosystems.

# Bring your own provider credentials

No live IBM/Azure keys are bundled in the repository.

Python setup:

```bash
qbt configure
qbt doctor
```

Rust setup:

```bash
cargo run -p qbt-bridge --bin qbt-rs -- configure
cargo run -p qbt-bridge --bin qbt-rs -- doctor
```

`.env` is gitignored. Secret fields use hidden terminal input. Doctor/status paths report configuration state without echoing raw secrets.

## IBM Quantum

Python:

```bash
pip install -e ".[ibm]"
qbt status --provider ibm
qbt sample --provider ibm --shots 1024
```

Rust:

```bash
export IBM_QUANTUM_TOKEN="..."
export IBM_QUANTUM_INSTANCE="..."
export IBM_QUANTUM_BACKEND="..."
cargo run -p qbt-bridge --bin qbt-rs -- sample --provider ibm --shots 1024
```

The native Rust path performs IBM IAM token exchange, Sampler V2 REST submission, polling, result retrieval, counts conversion, normalization, and QBT provenance.

## Azure Quantum

Python:

```bash
pip install -e ".[azure]"
qbt status --provider azure
```

Recommended workspace locator:

```dotenv
AZURE_QUANTUM_RESOURCE_ID=
AZURE_QUANTUM_TARGET=
```

Rust exposes `AzureRestClient`, `AzureRunner`, and `AzureQuantumProvider`, keeping target-specific job schemas at the provider edge while preserving the QBT state contract downstream.

See [`docs/API_KEYS.md`](docs/API_KEYS.md) and [`RUST_USERS.md`](RUST_USERS.md).

# Canonical normalized contract

Every successful provider sample becomes a `QuantumState` containing:

```text
qbt_version
provider
backend
execution_mode = hardware | simulator | archive | fallback
timestamp
job_id
shots
entropy in [0, 1]
normalized_vector[4]
result_digest = SHA-256
provenance
quality
```

A `ControlPacket` contains:

```text
qbt_version
active_sources
quantum_mix in [0, 1]
states[]
provider_errors{}
```

The four normalized vector dimensions are:

1. normalized Shannon entropy
2. hardware-source flag
3. logarithmic shot reliability
4. quality confidence

# Model integration

Python prompt-safe integration:

```python
from qbt_bridge.integrations import to_prompt_block
prompt_context = to_prompt_block(packet)
```

Optional PyTorch conditioner:

```python
from qbt_bridge.integrations.torch import build_qbt_conditioner
conditioner = build_qbt_conditioner(model_dim=4096, quantum_dim=4)
```

Conditioning rule:

```text
H_q = W_q Q + b_q
G   = sigmoid(W_g[H ; H_q] + b_g)
H'  = LayerNorm(H + G * H_q)
```

Other languages can consume the same normalized vector in their own tensor/runtime libraries.

# Scientific controls

Performance claims should compare at least:

1. real quantum hardware
2. provider simulator
3. matched classical random source
4. fixed control
5. QBT disabled

A provider connection, backend name, job ID, or physical random source can establish integration/provenance. It does **not** by itself establish improved model quality or quantum advantage.

# COSMOS proof-of-concept lineage

The source material from which QBT was extracted recorded:

- a COSMOS runtime connection to IBM backend `ibm_fez`
- a bridge-reported value `0.8239` in that captured run
- explicit hardware/simulation/archive status paths
- permission checks before explicit real IBM live-refill execution
- IBM/Azure entropy blending into a classical cognitive loop as bounded `q_entropy`

The broader CST/COSMOS research ledger reports positive evidence for quantum provenance/auditability while several matched ML-advantage tests were null. This repository preserves that distinction.

Related foundational research: **12-Dimensional Cosmic Synapse Theory**, DOI `10.5281/zenodo.17574447`.

# Repository map

```text
Cargo.toml                         Rust workspace
src/qbt_bridge/                    native Python SDK
rust/qbt-bridge/                   native Rust SDK
rust/qbt-ffi/                      C ABI / C++ wrapper
spec/                              JSON Schema + OpenAPI + protocol
bindings/                          cross-language reference clients
LANGUAGE_COMPATIBILITY.md          complete language matrix
RUST_USERS.md                      Rust manual
tests/                             Python tests
examples/                          Python examples
docs/API_KEYS.md                   BYOK setup
docs/ARCHITECTURE.md               architecture manual
docs/INTEGRATION_GUIDE.md          adoption guide
docs/PROOF_OF_CONCEPT.md           evidence/claim boundaries
docs/SECURITY.md                   security guidance
docs/TEACHER_MANUAL.md             teaching course/labs/rubric
docs/DISTRIBUTION.md               distribution guidance
docs/LAUNCH_KIT.md                 launch material
docs/DEMO_SCRIPT.md                demo sequence
paper/QUANTUM_BRIDGE_TRANSFORMER.md publication-style manuscript
RELEASE_CHECKLIST.md                release acceptance gates
```

# Validation

GitHub Actions is the source of truth for automated release validation. The compatibility suite covers:

- Python 3.10 / 3.11 / 3.12
- Rust workspace tests + Clippy + rustfmt
- Rust workspace tests on Windows and macOS
- linked C and C++ FFI executables
- sidecar smoke tests on Linux, Windows, and macOS
- JavaScript + TypeScript declarations
- Go
- Java / Kotlin-compatible JVM client
- C# / .NET
- Swift
- PHP
- Ruby
- Perl
- shell/curl
- PowerShell

Live IBM/Azure account acceptance remains BYOK and is never performed with somebody else's private credentials in public CI. HTTP-triggered live provider jobs require explicit operator opt-in.

# Contribute

Research feedback, reproducibility reports, security reports, documentation corrections, and citations are welcome. External code or copyrightable contributions are not accepted for incorporation unless written contribution rights are arranged first. See `CONTRIBUTING.md`.

# License

Current covered Cory-owned original material is distributed under the repository's restricted source rights notice. See `LICENSE`, `LICENSE_HISTORY.md`, and `COMMERCIAL_RIGHTS.md`.

Historical copies or versions that were validly distributed under Apache License 2.0 retain the rights granted to those copies. This current notice does not revoke those historical grants.

Copyright 2026 Cory Shane Davis.
