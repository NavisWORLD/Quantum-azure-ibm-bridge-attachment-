# Quantum Bridge Transformer: A Provider-Neutral Architecture for Bounded Quantum-Derived Control and Provenance in Classical AI Systems

**Cory Shane Davis**  
COSMOS / CST Research Lineage  
2026

## Abstract

This paper presents the Quantum Bridge Transformer (QBT), a provider-neutral software architecture for incorporating measured outputs from quantum-computing services into classical AI and control systems without conflating quantum execution with classical model inference. QBT separates provider execution, normalization, provenance, bounded control-state construction, and downstream conditioning. The reference implementation supports dependency-free classical controls and adapters for IBM Quantum and Azure Quantum, while preserving execution-mode labels and fail-soft behavior. The architecture was extracted from the COSMOS/CST runtime, where IBM/Azure quantum signals were used as entropy/provenance/control context alongside a classical stateful AI stack. A captured runtime demonstrated connection to IBM backend `ibm_fez` and a bridge value of `0.8239`; this establishes a proof of integration for that run, not quantum advantage. The broader research ledger reports positive evidence for auditable quantum provenance but null results for several matched ML-advantage tests. QBT is therefore proposed as an experimental and engineering standard whose value can be independently tested against simulator, classical-random, fixed, and disabled controls.

## 1. Introduction

"Quantum AI" is often used ambiguously. A classical transformer can consume data produced by a quantum computer without the transformer itself becoming a quantum neural network. The practical engineering problem is therefore not how to rename a classical model, but how to create a disciplined interface between two computational domains.

QBT addresses that interface.

The design goals are:

1. provider independence;
2. explicit hardware/simulator/archive/fallback labeling;
3. bounded normalized state;
4. provenance suitable for later audit;
5. graceful degradation;
6. multiple downstream integration levels;
7. falsifiable comparison against classical controls.

## 2. Architecture

The core pipeline is:

```text
quantum provider
  -> QuantumSample
  -> normalization
  -> QuantumState
  -> control projection/gating
  -> classical model or controller
```

A `QuantumSample` retains provider-native evidence such as counts, target/backend, shot count, job ID, and metadata. The bridge converts this into a normalized `QuantumState`.

## 3. Normalized entropy feature

For empirical probabilities `p_i` over `k` observed outcomes:

`H = -sum(p_i log2(p_i))`

and

`q = H / log2(k)`

when `k > 1`. The reference implementation clips the result to `[0,1]`.

This value is an engineering feature derived from the observed count distribution. It should not be interpreted as a complete measure of a device's quantum entropy or a certificate of quantumness.

## 4. Multi-provider state

For available normalized source values `q_1 ... q_n`:

`q_mix = clip(mean(q_i), 0, 1)`

If no source succeeds, the reference fallback is `0.5`.

The COSMOS source lineage used the same bounded averaging principle for active IBM/Azure bridge values before supplying `q_entropy` to a classical cognitive loop.

## 5. Transformer conditioning

Let the normalized quantum vector be `Q_t` and the classical hidden state be `H_t`.

Project:

`H_q = W_q Q_t + b_q`

Gate:

`G_t = sigmoid(W_g[H_t; H_q] + b_g)`

Condition:

`H'_t = LayerNorm(H_t + G_t * H_q)`

This formulation permits the learned gate to suppress an unhelpful quantum channel.

## 6. Three deployment levels

### 6.1 Prompt metadata

Serialize only non-secret normalized state into structured context. This requires no model retraining.

### 6.2 External controller

Use bounded state for routing, exploration, ensemble selection, or simulation initialization.

### 6.3 Native conditioner

Train the projection and gate inside a neural model.

## 7. COSMOS proof of concept

A captured COSMOS runtime recorded:

```text
[QUANTUM] Connected to REAL backend: ibm_fez
Quantum Bridge Active | Entropy Source: ibm_fez | Value: 0.8239
```

The broader source also exposed:

- quantum status;
- explicit live-refill routes;
- simulation distinction;
- archive replay;
- Azure Quantum status;
- permission checks before explicit real IBM refill;
- a `q_entropy` path into the classical cognitive loop.

This supports the engineering claim that the bridge was integrated into a running classical AI system.

It does not establish that the quantum input improved model quality.

## 8. Evidence from the broader research lineage

The associated research ledger distinguishes architecture results from quantum-advantage claims.

### 8.1 Provenance-positive findings

Reported evidence includes:

- CHSH `S = 2.7905` on `ibm_marrakesh` in the cited run;
- archived bitstring-to-weight distribution checks;
- deterministic re-creation from a fixed stored seed;
- sensitivity to a one-bit seed change;
- relocation of measured correlation structure when programmed logical topology was changed under matched hardware.

These results support provenance and physical-source validation questions.

### 8.2 ML-advantage nulls

The ledger reports no supported accuracy advantage in tested comparisons for:

- quantum versus classical initialization;
- quantum versus classical decoder seed;
- quantum spatial/54D state seeds;
- a measured entanglement-derived attention kernel, which underperformed plain attention in the cited matched test.

The current supported conclusion is therefore narrower:

> Quantum-derived signals can supply auditable physical provenance and bounded nondeterministic/control inputs; generalized ML performance advantage has not been established.

## 9. Related non-quantum state result

The associated CST transformer research reported a corrected seven-rung state ladder over 21 runs. `dyn12` achieved mean validation loss `1.17897` versus baseline `1.23241`, winning all three cited seeds and using approximately `1,137,420` parameters.

This demonstrates that compact state-conditioned attention can be useful in that tested architecture. It must not be used as evidence that quantum conditioning caused the improvement.

## 10. Required experimental controls

A serious QBT evaluation should compare:

1. hardware quantum result;
2. provider simulator;
3. matched classical random source;
4. fixed scalar/vector;
5. QBT disabled.

All other model, dataset, optimizer, and decoding variables should remain fixed.

## 11. Reproducibility record

For each inference or experiment, record:

- provider/backend;
- job ID;
- timestamp;
- shots;
- program/circuit digest;
- result digest;
- normalized QBT packet;
- host model/checkpoint hash;
- dataset snapshot;
- software versions;
- random seeds;
- measured cost/latency;
- control-arm label.

## 12. Security

Credentials are not model context. Provider tokens must remain server-side. Real hardware calls should be policy gated because they may incur cost and queue time.

## 13. Limitations

The current reference implementation does not claim:

- universal provider schema compatibility;
- hardware-independent physical entropy certification;
- quantum advantage;
- consciousness;
- superior prediction;
- a quantum implementation of the transformer itself.

Azure Quantum is intentionally represented through a workspace plus provider-specific injected runner because Azure targets differ in submission/result format.

## 14. Conclusion

QBT is a practical boundary layer between quantum measurements and classical AI. Its contribution is architectural discipline: provenance, bounded normalization, provider abstraction, explicit control modes, and falsifiable experiments. The reference implementation is designed so a company can adopt the bridge without adopting the broader COSMOS runtime.

## 15. Foundational related work

Cory Shane Davis, **12-Dimensional Cosmic Synapse Theory**, Zenodo, DOI: `10.5281/zenodo.17574447`.

Additional public evidence and benchmark artifacts are maintained in the COSMOS/CST project lineage and the QC67_cosmo release.
