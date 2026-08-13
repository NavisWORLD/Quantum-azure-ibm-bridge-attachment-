# Teacher Manual — Quantum Bridge Transformer

## Audience

Upper-level high-school, undergraduate, graduate, professional engineering, or internal company training. Instructors may simplify the mathematics for younger groups while preserving the same evidence discipline.

## Learning objectives

By the end of the module, students should be able to:

1. distinguish a QPU from a classical AI model;
2. explain why a bridge layer is needed;
3. implement a provider-neutral interface;
4. normalize a measured distribution into a bounded feature;
5. preserve provenance;
6. build hardware/simulator/classical/fixed/disabled controls;
7. explain the difference between quantum provenance and quantum advantage;
8. integrate a bounded control vector into a transformer or controller;
9. design an experiment that can return a valid null result.

## Core analogy

A QPU is not "the chatbot brain." It is more like a laboratory instrument that returns measurements. QBT is the translator and receipt system between the instrument and the ordinary software.

## Suggested 8-session course

### Session 1 — Hybrid computing
Teach classical inference vs quantum execution. Whiteboard the pipeline.

### Session 2 — Probability and counts
Use `SimulatorProvider`. Explain shots, empirical probability, Shannon entropy, and normalization.

### Session 3 — Provenance
Inspect `QuantumState`. Hash the same payload twice, then alter one count and observe the digest change.

### Session 4 — Fail-soft systems
Use the broken-provider test. Discuss why external scientific services must not become single points of failure.

### Session 5 — Prompt/controller integration
Use `to_prompt_block()`. Ask students to identify which fields are safe for a model and which secrets must remain outside.

### Session 6 — Native neural gate
Use the PyTorch conditioner. Discuss why sigmoid gating is safer than directly adding an unbounded provider result.

### Session 7 — Controls and falsification
Design five matched arms: hardware, simulator, classical random, fixed, disabled.

### Session 8 — Research presentation
Students defend one narrow claim and one null result.

## Labs

### Lab A — Entropy extremes

Run:

```python
entropy_from_counts({"0": 100})
entropy_from_counts({"0": 50, "1": 50})
```

Expected conceptual answer:

- first case: no observed uncertainty -> normalized entropy `0`
- second case: maximum uncertainty across the two observed outcomes -> `1`

### Lab B — Provenance tamper test

Create a `QuantumSample`, normalize it, modify one count, normalize again.

Expected result: result digests differ.

### Lab C — Provider failure

Create a provider whose `sample()` raises an exception.

Expected result: the host bridge returns zero active sources and the configured fallback instead of crashing.

### Lab D — Control equivalence

Run one downstream toy task with:

- seeded simulator
- another seeded PRNG
- fixed 0.5
- disabled signal

Ask whether any performance difference is larger than ordinary run-to-run variation.

### Lab E — Gate ablation

Train or mock a QBT gate. Compare:

- gate fixed at zero
- learnable gate
- gate fixed at one

Explain why the learnable gate is the scientifically interesting arm.

### Lab F — Claim audit

Give students these statements:

1. "The IBM job ID proves a specific quantum job was referenced."
2. "The IBM job ID proves the model became more accurate."
3. "A CHSH violation validates the quantum character of the measured source under that test."
4. "A CHSH violation proves quantum advantage for language modeling."

Correct: 1 and 3 can be supportable with the corresponding evidence; 2 and 4 are category errors.

## Instructor answer guide

### Why normalize?

Provider-native outputs differ by backend, shot count, and outcome space. A bounded representation makes integration safer and testable.

### Why preserve mode labels?

A simulator result and hardware result can look structurally similar. Without labels, later experiments cannot distinguish them.

### Why use null controls?

Randomness from two sources can have the same distribution. If quantum randomness is claimed to improve an ML metric, the experiment must show an effect beyond matched classical randomness.

### Why can a null be useful?

It prevents the architecture from accumulating false claims. A null can still validate the bridge, provenance, cost model, and experiment harness.

## Oral exam rubric

| Criterion | Excellent | Needs revision |
|---|---|---|
| Architecture | Separates QPU, bridge, conditioner, host model | Calls whole system "quantum AI" |
| Provenance | Names provider/backend/job/hash/mode | Uses visual labels as proof |
| Statistics | Includes matched controls and multiple seeds/runs | Compares one hardware run to one baseline |
| Claim discipline | Distinguishes integration, provenance, advantage | Treats connection as performance proof |
| Safety | Protects secrets and bounds external inputs | Puts tokens in code/prompt |
| Engineering | Handles provider failure | Lets QPU outage crash host app |

## Capstone assignment

Build a QBT attachment for an existing small AI or simulation project. The submission must contain:

- provider abstraction
- simulator/control provider
- one optional hardware provider
- normalized packet
- provenance digest
- fail-soft test
- five-arm experimental plan
- a one-page claim map separating observed, measured, null, and speculative statements
