# Quantum Azure + IBM Bridge Attachment

A reusable, provider-neutral implementation of the **Quantum Bridge Transformer (QBT)** integration pattern developed in the COSMOS/CST research lineage.

> **Core claim:** QBT lets classical AI, control systems, agents, and transformers consume bounded, auditable signals derived from quantum-computing executions. It does **not** claim that the downstream language model itself runs on a QPU, and this repository does **not** claim quantum advantage for ML.

## Why this repository exists

The original COSMOS runtime used IBM/Azure quantum systems as entropy, provenance, and control channels alongside classical state, memory, sensory summaries, and local model inference. This repository extracts that pattern into a small library that another engineer or company can add to an unrelated project.

```text
IBM Quantum ──┐
              ├──> Provider adapters
Azure Quantum ┤          │
Simulator ────┘          ▼
                  QuantumBridge
                       │
            normalized QuantumState
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
      Prompt block  Controller   QBT gate
                                  │
                                  ▼
                           Classical model
```

## Install

Core + simulator:

```bash
pip install -e .
```

IBM Quantum:

```bash
pip install -e ".[ibm]"
```

Azure Quantum:

```bash
pip install -e ".[azure]"
```

PyTorch conditioning layer:

```bash
pip install -e ".[torch]"
```

Development:

```bash
pip install -e ".[dev]"
pytest
```

## 60-second integration

```python
from qbt_bridge import QuantumBridge
from qbt_bridge.providers import SimulatorProvider

bridge = QuantumBridge([SimulatorProvider(seed=7)])
bridge.connect()

packet = bridge.control_packet(shots=2048)

print(packet["quantum_mix"])
print(packet["states"][0]["result_digest"])
```

The simulator is intentionally a **classical control**. Its output is labeled `simulator`, never hardware.

## IBM integration

```python
from qbt_bridge import QuantumBridge
from qbt_bridge.providers.ibm import IBMQuantumProvider

provider = IBMQuantumProvider(
    backend="YOUR_BACKEND"  # optional; otherwise adapter selects an operational backend
)

bridge = QuantumBridge([provider])
print(bridge.connect())
packet = bridge.control_packet(shots=1024)
```

Set credentials outside source control:

```bash
export IBM_QUANTUM_TOKEN="..."
```

## Azure integration

Azure Quantum exposes multiple provider/target styles, so the package keeps the provider-specific submission logic behind an injected runner:

```python
from qbt_bridge import QuantumBridge
from qbt_bridge.providers.azure import AzureQuantumProvider

def run_azure(workspace, target, shots):
    # Submit through the Azure provider SDK appropriate to your target.
    # Return the normalized minimum contract shown below.
    return {
        "counts": {"0": 510, "1": 514},
        "job_id": "provider-job-id",
        "backend": target,
        "quality_class": "hardware",
    }

provider = AzureQuantumProvider(runner=run_azure)
bridge = QuantumBridge([provider])
bridge.connect()
packet = bridge.control_packet(shots=1024)
```

This design avoids pretending all Azure targets share one job schema.

## Minimum normalized contract

Every provider is converted into a `QuantumState` containing:

- provider
- backend
- execution mode: `hardware`, `simulator`, `archive`, or `fallback`
- timestamp
- job ID when available
- shots
- normalized entropy in `[0, 1]`
- normalized control vector
- SHA-256 result digest
- non-secret provenance
- quality metadata

## Three integration levels

### 1. Prompt/control context

Use `qbt_bridge.integrations.to_prompt_block(packet)` to give a model compact, auditable state without exposing credentials.

### 2. External controller

Use `quantum_mix` or the full normalized vector to choose a search branch, ensemble route, exploration policy, simulation parameter, or other bounded control.

### 3. Native transformer conditioner

`build_qbt_conditioner()` implements:

\[
H_q = W_q Q + b_q
\]

\[
G = \sigma(W_g[H;H_q] + b_g)
\]

\[
H' = LayerNorm(H + G \odot H_q)
\]

If training finds no value in the quantum channel, the gate can learn toward zero.

## Scientific controls are mandatory

For research claims, compare at least:

1. real quantum hardware
2. provider simulator
3. matched classical CSPRNG/PRNG
4. fixed `0.5` control
5. QBT disabled

A bridge connection proves integration and provenance. It does **not** prove an accuracy advantage.

## COSMOS proof-of-concept lineage

The source material used to extract this library recorded:

- a live COSMOS boot connecting to IBM backend `ibm_fez`
- bridge-reported entropy value `0.8239` in that run
- separate hardware/simulation/archive status paths
- explicit user-triggered IBM live-refill permission checks
- fail-soft bridge behavior
- IBM/Azure entropy blending into the COSMOS cognitive loop as bounded `q_entropy`

See `docs/PROOF_OF_CONCEPT.md` and `paper/QUANTUM_BRIDGE_TRANSFORMER.md`.

## Research status

The broader CST/COSMOS research ledger reports positive results for **quantum provenance and auditability**, while matched tests did **not** establish quantum advantage for model accuracy. This repository preserves that distinction on purpose.

Related foundational research: **12-Dimensional Cosmic Synapse Theory**, DOI `10.5281/zenodo.17574447`.

## Documentation

- `docs/ARCHITECTURE.md` — engineering architecture
- `docs/INTEGRATION_GUIDE.md` — company/project integration checklist
- `docs/PROOF_OF_CONCEPT.md` — evidence and claim boundaries
- `docs/TEACHER_MANUAL.md` — curriculum, labs, rubric, answer guidance
- `docs/SECURITY.md` — credentials, privacy, permissions
- `paper/QUANTUM_BRIDGE_TRANSFORMER.md` — publication-style manuscript
- `CITATION.cff` — citation metadata

## License

Apache License 2.0. See `LICENSE`.

Copyright 2026 Cory Shane Davis.
