# QBT Architecture

## 1. Purpose

The Quantum Bridge Transformer (QBT) is a hybrid interface, not a claim that a conventional transformer executes on quantum hardware.

```text
Quantum execution
      ↓
provider-native result
      ↓
QuantumSample
      ↓
normalization + digest + provenance
      ↓
QuantumState
      ↓
bounded control / projection / gate
      ↓
classical AI or control system
```

## 2. Separation of responsibilities

### Provider
Submits or retrieves a quantum execution and returns raw counts plus provider metadata.

### Bridge
Normalizes, validates, hashes, blends, and fails safely.

### Integration
Consumes the state at one of three levels: prompt, external controller, or trainable neural conditioner.

### Host model
Performs the actual downstream inference.

## 3. Entropy normalization

For observed outcome probabilities `p_i`, normalized Shannon entropy is:

`q = (-sum(p_i * log2(p_i))) / log2(k)`

for `k > 1` observed positive-probability outcomes. `q` is clipped to `[0,1]`.

This is an engineering normalization, not a complete physical measure of quantum entropy.

## 4. Multi-provider blend

For valid finite values `q_i`:

`q_mix = clip(mean(q_i), 0, 1)`

If no provider succeeds, the bridge returns a configurable fallback, default `0.5`.

This mirrors the fail-soft design extracted from COSMOS: a quantum outage must not crash ordinary inference.

## 5. Native neural conditioning

A host model can project the normalized quantum vector `Q_t`:

`H_q = W_q Q_t + b_q`

and learn a bounded gate:

`G_t = sigmoid(W_g[H_t; H_q] + b_g)`

`H'_t = LayerNorm(H_t + G_t * H_q)`

The gate is important because it gives training an explicit path to suppress useless quantum context.

## 6. Provenance

Every sample should preserve:

- provider
- backend
- job ID
- execution mode
- shot count
- timestamp
- result digest
- provider metadata that does not contain credentials

For high-assurance use, add circuit/program digest, SDK version, target calibration snapshot, and immutable storage.

## 7. Replay

A production system should store normalized records so the same downstream experiment can be replayed without paying for fresh QPU time.

Recommended modes:

- `hardware`
- `simulator`
- `archive`
- `fallback`

Never collapse these into one unlabeled field.

## 8. Failure model

Provider errors are isolated. The bridge:

1. records provider unavailability in status;
2. skips failed sources during sampling;
3. retains a bounded fallback;
4. never exposes credentials in the control packet.

## 9. What QBT does not establish

QBT does not, by itself, establish:

- quantum advantage
- superior model accuracy
- consciousness
- quantum cognition
- entanglement between a user and AI
- physical interpretations of CST

Those require independent experiments.
