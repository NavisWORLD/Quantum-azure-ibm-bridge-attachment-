# Integration Guide

## Goal

Attach QBT to an existing project with the smallest possible trust surface.

## Step 1 — Choose the integration level

**Prompt level:** no model surgery. Best for prototyping.

**Controller level:** use a scalar/vector to affect routing, exploration, simulation, or ensemble selection.

**Native layer:** add the QBT conditioner to a neural model and train the gate.

## Step 2 — Start with the simulator

```python
from qbt_bridge import QuantumBridge
from qbt_bridge.providers import SimulatorProvider

bridge = QuantumBridge([SimulatorProvider(seed=123)])
bridge.connect()
packet = bridge.control_packet(shots=1024)
```

Build your whole host integration against this first.

## Step 3 — Add one hardware provider

Do not add IBM and Azure simultaneously on the first hardware test. Validate one provider path, provenance record, timeout behavior, and cost policy first.

## Step 4 — Protect credentials

Use environment variables, a secret manager, workload identity, or provider-native credentials.

Never:

- commit tokens
- include tokens in QBT packets
- put credentials in model prompts
- expose them to browser code

## Step 5 — Define the control policy

Write down exactly what quantum state may influence.

Good examples:

- selecting among equivalent search branches
- stochastic exploration
- simulation initial conditions
- ensemble routing
- research feature-conditioning

Avoid letting an unbounded raw provider result directly overwrite model activations or silently changing business-critical decisions without audit logs.

## Step 6 — Add matched controls

Every experiment should make it possible to swap:

```text
hardware
simulator
classical PRNG/CSPRNG
fixed scalar
disabled
```

without changing the rest of the stack.

## Step 7 — Persist provenance

Store the normalized state and its digest beside the host inference/decision ID.

## Step 8 — Set cost and permission gates

Real QPU calls can cost money and may queue. In production, require explicit policy checks before new jobs are submitted.

## Step 9 — Test provider failure

Your host application should still work when every quantum provider is offline.

## Step 10 — Report claims correctly

Acceptable:

> The system used a measured IBM Quantum job as a control/provenance input.

Not acceptable without an experiment:

> The quantum computer made the AI smarter.

## Company checklist

- [ ] Threat model reviewed
- [ ] Secrets are server-side
- [ ] Execution mode is labeled
- [ ] Provider job ID is retained
- [ ] Result hash is retained
- [ ] Fallback behavior is tested
- [ ] QPU cost limit exists
- [ ] Simulator/control path exists
- [ ] Hardware-vs-control benchmark is predeclared
- [ ] No marketing claim exceeds measured evidence
