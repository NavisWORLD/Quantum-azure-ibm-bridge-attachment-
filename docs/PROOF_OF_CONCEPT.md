# Proof of Concept and Evidence Ledger

## Scope

This document records the engineering evidence that motivated extraction of QBT from the broader COSMOS/CST project. It separates **observed implementation evidence** from **generalized architecture**.

## Observed runtime evidence

A captured COSMOS runtime log recorded:

```text
[QUANTUM] Attempting connection to IBM Quantum.
[QUANTUM] Connected to REAL backend: ibm_fez
Quantum Bridge Active | Entropy Source: ibm_fez | Value: 0.8239
```

This is evidence that the runtime established a provider connection and obtained a bridge value in that run. It is not evidence of quantum advantage.

## Observed software path

The COSMOS source exposed:

- `/api/quantum/status`
- `/api/quantum/archive-status`
- `/api/quantum/live-refill`
- Azure Quantum status/harvest paths
- provider state including active/simulation/backend/error information
- explicit permission evaluation before a real IBM live-refill call
- archive/replay metadata
- a bounded quantum blend used as `q_entropy`

The cognitive loop received `q_entropy` alongside classical state such as prompt, user physics/state, chaos state, audio energy, and dominant frequency.

## Extracted invariant

```text
provider execution
  -> measured result
  -> normalized bounded state
  -> provenance
  -> optional classical-model conditioning
```

The reusable library in this repository implements this invariant without depending on COSMOS.

## Broader research findings that constrain claims

### Positive / supported

- Quantum measurement provenance can be retained and audited.
- A reported CHSH run on `ibm_marrakesh` produced `S = 2.7905` versus the classical bound `2.0` in the cited experiment.
- Archived quantum-derived bitstring-to-weight mapping was checked for distributional consistency.
- Identical recorded seed reproduced identical initialization; a one-bit seed change altered the initialization.
- Programmed topology changes were reported to relocate measured correlation structure under matched hardware.

### Null / unsupported advantage claims

Matched tests did **not** establish model-quality advantage from:

- quantum initialization versus classical initialization
- quantum decoder seed versus classical seed
- quantum spatial/54D seeds
- a measured entanglement kernel for the cited attention objective

Therefore the correct current claim is:

> Quantum-derived signals provide auditable physical provenance and nondeterministic/control inputs. A general ML accuracy advantage has not been established.

## Related transformer result, not a quantum-advantage result

The corrected seven-rung CST state ladder (21 runs, three seeds per rung) reported approximately:

| Rung | Mean validation loss | Delta vs baseline | Wins | Approx. params |
|---|---:|---:|---:|---:|
| dyn12 | 1.17897 | -0.0534 | 3/3 | 1,137,420 |
| dyn54 | 1.18791 | -0.0445 | 3/3 | 1,185,174 |
| static54 | 1.18824 | -0.0442 | 3/3 | 1,176,480 |
| dyn42 | 1.19020 | -0.0422 | 3/3 | 1,182,762 |
| tri | 1.19247 | -0.0399 | 3/3 | 1,189,210 |
| tri3 | 1.20026 | -0.0322 | 3/3 | 1,230,682 |
| none | 1.23241 | baseline | 0/3 | 1,135,008 |

This result concerns compact state-conditioned attention. It should not be presented as evidence that quantum signals improved the transformer.

## Reproduction requirements

A new QBT experiment should record:

- provider
- target/backend
- job ID
- timestamp
- shots
- circuit/program hash
- returned counts/result hash
- normalized state
- host model/checkpoint hash
- dataset snapshot hash
- random seeds
- control-arm definition
- task metric
- cost and latency

## Foundational reference

Cory Shane Davis, *12-Dimensional Cosmic Synapse Theory*, Zenodo DOI:

`10.5281/zenodo.17574447`
