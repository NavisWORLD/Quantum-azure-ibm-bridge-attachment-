# Quantum Bridge Transformer (QBT)

[![CI](https://github.com/NavisWORLD/Quantum-azure-ibm-bridge-attachment-/actions/workflows/ci.yml/badge.svg)](https://github.com/NavisWORLD/Quantum-azure-ibm-bridge-attachment-/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Rust](https://img.shields.io/badge/Rust-native-orange)
![License](https://img.shields.io/badge/license-Apache--2.0-green)
![IBM Quantum](https://img.shields.io/badge/IBM-Quantum-6929C4)
![Azure Quantum](https://img.shields.io/badge/Azure-Quantum-0078D4)

> **Bring your own quantum account. Keep your own AI stack.**

QBT is a reusable, provider-neutral attachment that converts IBM Quantum / Azure Quantum execution results into bounded, auditable control state that ordinary AI, agents, simulations, and control systems can consume.

The repository now ships **two first-class implementations: Python and native Rust**. The Rust crate is not a Python subprocess wrapper; it implements the QBT state model, provider trait, normalization, provenance hashing, fail-soft bridge, simulator, IBM REST flow, Azure REST/runner layer, CLI, tests, and examples directly in Rust.

It does **not** claim that your LLM suddenly runs on a QPU. It gives your existing software a disciplined quantum-to-classical interface.

```text
IBM Quantum ──┐
              ├──> QBT provider adapters
Azure Quantum ┤          │
Simulator ────┘          ▼
                  normalized QuantumState
                       │
        provenance + bounded control vector
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       prompts       routing     model gate
                                    │
                                    ▼
                              your AI/model
```

## Why engineers use it

- **Python + native Rust** — choose the host language that fits your stack.
- **Bring your own keys/account** — no COSMOS credentials are bundled or required.
- **IBM + Azure** — IBM Qiskit Runtime/Sampler V2 in Python, IBM REST in Rust, and Azure workspace/data-plane integration paths.
- **Provider-neutral contract** — downstream code consumes `QuantumState`, not vendor SDK objects.
- **Auditable provenance** — provider, backend, job ID, shot count, timestamp, and SHA-256 digest.
- **Bounded influence** — normalized vectors and optional learned gating instead of raw unbounded injection.
- **Fail-soft** — QPU/provider outages do not have to crash normal inference.
- **Scientifically testable** — hardware, simulator, classical-random, fixed, and disabled control arms are first-class.
- **Easy to teach** — teacher manual, labs, paper, proof ledger, and demo script included.

# Python quick start

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

The default sample is deliberately a **classical control** and is labeled `simulator`.

# Rust quick start

The repository root is a Cargo workspace, so Rust users can start immediately:

```bash
git clone https://github.com/NavisWORLD/Quantum-azure-ibm-bridge-attachment-.git
cd Quantum-azure-ibm-bridge-attachment-
cargo test --workspace
cargo run -p qbt-bridge --bin qbt-rs -- sample --provider simulator --shots 1024
```

Or use the crate in another Rust project as a path dependency:

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
    println!("digest={}", packet.states[0].result_digest);
    Ok(())
}
```

See **[`RUST_USERS.md`](RUST_USERS.md)** for IBM REST, Azure REST/runner, custom provider, configuration, and production guidance.

# Bring your own API keys

Python interactive setup:

```bash
qbt configure
qbt doctor
```

`qbt configure` writes a local `.env` file that is gitignored. Secret fields use hidden terminal input. `qbt doctor` reports only `configured` / `missing` for secrets; it does not print them.

You can also copy the template:

```bash
cp .env.example .env
```

Rust has its own CLI:

```bash
cargo run -p qbt-bridge --bin qbt-rs -- doctor
cargo run -p qbt-bridge --bin qbt-rs -- configure
```

## IBM Quantum — Python

Install:

```bash
pip install -e ".[ibm]"
```

Configure one of these ways:

1. `qbt configure`
2. environment variables
3. a Qiskit Runtime account already saved on your machine
4. direct constructor injection from your organization's secret manager

Environment variables:

```dotenv
IBM_QUANTUM_TOKEN=
IBM_QUANTUM_INSTANCE=
IBM_QUANTUM_BACKEND=
```

Then:

```bash
qbt status --provider ibm
qbt sample --provider ibm --shots 1024
```

```python
from qbt_bridge import QuantumBridge
from qbt_bridge.providers.ibm import IBMQuantumProvider

bridge = QuantumBridge([IBMQuantumProvider()])
print(bridge.connect())
packet = bridge.control_packet(shots=1024)
print(packet["quantum_mix"])
print(packet["states"][0]["job_id"])
```

## IBM Quantum — Rust

Rust uses IBM's language-neutral REST interface. Supply your own IBM API key and Quantum Compute instance CRN:

```bash
export IBM_QUANTUM_TOKEN="..."
export IBM_QUANTUM_INSTANCE="..."
export IBM_QUANTUM_BACKEND="..."
cargo run -p qbt-bridge --bin qbt-rs -- sample --provider ibm --shots 1024
```

The Rust provider performs IBM IAM token exchange, submits a Sampler V2 REST job, polls job state, retrieves samples, converts them to counts, and emits a normalized QBT packet. Advanced users can provide pre-transpiled/ISA OpenQASM through `IBM_QUANTUM_QASM`. See `RUST_USERS.md`.

## Azure Quantum — Python

Install:

```bash
pip install -e ".[azure]"
```

Recommended workspace locator:

```dotenv
AZURE_QUANTUM_RESOURCE_ID=
AZURE_QUANTUM_TARGET=
```

Alternative locator:

```dotenv
AZURE_SUBSCRIPTION_ID=
AZURE_QUANTUM_RESOURCE_GROUP=
AZURE_QUANTUM_WORKSPACE=
```

Optional Microsoft Entra service principal:

```dotenv
AZURE_TENANT_ID=
AZURE_CLIENT_ID=
AZURE_CLIENT_SECRET=
```

Azure CLI / DefaultAzureCredential can be used instead, avoiding a stored client secret.

```bash
qbt status --provider azure
```

Azure Quantum supports multiple target/provider job schemas, so QBT keeps execution behind a tiny injected runner instead of pretending every target has the same `run()` API. See `docs/API_KEYS.md` and `examples/azure_workspace.py`.

## Azure Quantum — Rust

Rust exposes:

- `AzureRestClient` for the Azure Quantum data-plane jobs API.
- `AzureRunner` for target-specific execution/result conversion.
- `AzureQuantumProvider` for feeding runner results into the normal QBT state/provenance pipeline.

This keeps vendor-specific payloads at the edge while preserving one QBT contract downstream. See `RUST_USERS.md` for complete examples.

# Five-line Python integration

```python
from qbt_bridge import QuantumBridge
from qbt_bridge.providers import SimulatorProvider

bridge = QuantumBridge([SimulatorProvider(seed=7)])
bridge.connect()
packet = bridge.control_packet(shots=2048)
```

`packet` contains the bounded multi-provider mix plus per-source provenance.

# Minimum normalized contract

Every provider becomes a `QuantumState` with:

```text
provider
backend
execution_mode = hardware | simulator | archive | fallback
timestamp
job_id
shots
entropy in [0, 1]
normalized_vector
result_digest (SHA-256)
provenance
quality metadata
```

The Python and Rust implementations intentionally use the same conceptual boundary so mixed-language services can exchange QBT packets over JSON.

# Three integration levels

## 1. Prompt/control metadata

Python includes:

```python
from qbt_bridge.integrations import to_prompt_block
prompt_context = to_prompt_block(packet)
```

Only non-secret state is serialized.

## 2. External controller

Use `quantum_mix` or the normalized vector to influence bounded routing, exploration, simulation initial conditions, or ensemble selection.

## 3. Native model conditioner

Python includes a PyTorch conditioner:

```python
from qbt_bridge.integrations.torch import build_qbt_conditioner
conditioner = build_qbt_conditioner(model_dim=4096, quantum_dim=4)
```

The conditioning rule is:

```text
H_q = W_q Q + b_q
G   = sigmoid(W_g[H ; H_q] + b_g)
H'  = LayerNorm(H + G * H_q)
```

Rust applications can feed the same `normalized_vector` into their own tensor/runtime layer without depending on Python.

# Scientific controls are mandatory for performance claims

Compare at least:

1. real quantum hardware
2. provider simulator
3. matched classical random source
4. fixed control
5. QBT disabled

A provider connection or job ID can establish integration/provenance. It does **not** establish a model-quality advantage.

# COSMOS proof-of-concept lineage

The source material from which QBT was extracted recorded:

- a COSMOS runtime connection to IBM backend `ibm_fez`
- a bridge-reported value `0.8239` in that captured run
- explicit hardware/simulation/archive status paths
- permission checks before explicit real IBM live-refill execution
- IBM/Azure entropy blending into a classical cognitive loop as bounded `q_entropy`

The broader CST/COSMOS research ledger reports positive evidence for quantum provenance/auditability while several matched ML-advantage tests were null. This repo preserves that distinction.

Related foundational research: **12-Dimensional Cosmic Synapse Theory**, DOI `10.5281/zenodo.17574447`.

# Repo map

```text
Cargo.toml                    root Rust workspace
src/qbt_bridge/               installable Python library
  bridge.py                   orchestration / fail-soft blend
  config.py                   BYOK .env loader + masked configuration status
  providers/ibm.py            IBM Qiskit Runtime / Sampler V2
  providers/azure.py          Azure Quantum workspace adapter
  providers/simulator.py      classical control
  integrations/prompt.py      prompt-safe state block
  integrations/torch.py       trainable conditioner
rust/qbt-bridge/              native Rust crate
  Cargo.toml                  Rust package metadata
  src/lib.rs                  QBT types/core/providers/REST clients
  src/bin/qbt-rs.rs           Rust CLI
  tests/                      Rust integration tests
  examples/                   Rust examples
RUST_USERS.md                 complete Rust integration manual
examples/                     Python integration examples
tests/                        Python offline tests
docs/API_KEYS.md              Python credential setup
docs/ARCHITECTURE.md          engineering specification
docs/INTEGRATION_GUIDE.md     company adoption checklist
docs/PROOF_OF_CONCEPT.md      evidence + claim boundaries
docs/TEACHER_MANUAL.md        course/labs/rubric/capstone
docs/LAUNCH_KIT.md            public launch copy + visual plan
docs/DEMO_SCRIPT.md           two-minute demo
paper/                        publication-style manuscript
```

# Launch / contribute

If you can add a provider, reproduce a benchmark, find a security issue, produce a clean null result, add a Rust/Python integration, or attach QBT to a model stack we did not anticipate, contributions are welcome. See `CONTRIBUTING.md` and `ROADMAP.md`.

# License

Apache License 2.0. See `LICENSE` and `NOTICE`.

Copyright 2026 Cory Shane Davis.
