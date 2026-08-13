# Public Launch Kit

This file contains launch copy that maintainers can adapt when releasing QBT publicly. Keep claims tied to what the repository actually demonstrates.

## One-line pitch

**Attach IBM Quantum or Azure Quantum to an existing classical AI project through one bounded, auditable provider-neutral control interface.**

## Short technical pitch

Quantum Bridge Transformer (QBT) turns provider-native quantum execution results into a normalized `QuantumState` with explicit hardware/simulator labeling, provenance hashes, fail-soft behavior, and optional transformer conditioning. Bring your own IBM/Azure credentials; keep your existing model.

## GitHub description

Provider-neutral IBM + Azure Quantum bridge for classical AI: BYOK credentials, provenance, bounded entropy/control state, simulator controls, and optional PyTorch transformer gating.

## Suggested GitHub topics

```text
quantum-computing
ibm-quantum
azure-quantum
qiskit
qdk
artificial-intelligence
transformers
pytorch
provenance
hybrid-computing
open-source
research
```

## README hero language

> **Bring your own quantum account. Keep your own AI stack.**
>
> QBT is a detachable bridge between measured quantum executions and ordinary software.

## X / short-form launch draft

I open-sourced the Quantum Bridge Transformer attachment from my COSMOS/CST work.

Bring your own IBM Quantum or Azure Quantum account. QBT turns provider results into bounded, auditable control state that can plug into an existing AI project without pretending the LLM itself runs on a QPU.

Simulator controls, provenance hashes, PyTorch gating, tests, teacher manual, and the research paper are included.

## LinkedIn launch draft

I have released the Quantum Bridge Transformer (QBT) as a standalone open-source integration kit.

The goal is straightforward: an engineering team should be able to connect its own IBM Quantum or Azure Quantum account to an existing classical AI or control system without adopting my entire COSMOS runtime.

QBT separates the layers cleanly: provider execution, normalized quantum state, provenance, bounded control, and downstream classical inference. The repository includes bring-your-own-key configuration, IBM and Azure adapters, simulator controls, a PyTorch conditioning layer, tests, security guidance, a teacher manual, and a publication-style paper.

I have also kept the research claims deliberately narrow. The project demonstrates an auditable quantum-to-classical integration path; it does not claim that a QPU automatically improves model accuracy. The included experimental guide shows exactly how to test hardware against simulator, classical-random, fixed, and disabled controls.

If you build on it, fork it, break it, benchmark it, or wire it into something I did not anticipate, that is the point.

## Hacker News / technical community draft

**Show HN: QBT — a provider-neutral IBM/Azure Quantum control bridge for classical AI**

I extracted the quantum bridge portion of a larger local AI project into a standalone Python package. It normalizes quantum job results into a bounded state, preserves provider/backend/job provenance, distinguishes hardware from simulator/replay, fails safely when providers are offline, and includes an optional PyTorch projection/gating layer.

It is deliberately not marketed as "quantum makes LLMs smarter." The repo includes matched-control guidance and documents null ML-advantage results from the broader research lineage.

The interesting question is narrower: can quantum-generated measurements become a clean, auditable, swappable control channel in ordinary software, and when does that channel actually help?

## Demo GIF/video storyboard

1. Clone the repository.
2. Run `qbt configure`.
3. Show the credential wizard without revealing entered secrets.
4. Run `qbt doctor` and show masked/configured status.
5. Run simulator sample and display the normalized packet.
6. Switch to IBM or Azure configuration.
7. Display provider/backend/job ID + digest.
8. Feed the four-value vector through the PyTorch conditioner.
9. End on the five experimental control arms.

## Viral-friendly technical visuals to create

- one architecture diagram: `IBM / Azure -> QBT -> your AI`
- one 15-second terminal demo
- one `hardware vs simulator vs PRNG vs fixed vs disabled` experiment card
- one code screenshot of the 5-line basic integration
- one screenshot of `qbt doctor` proving secrets are masked

The visual hook should be **simplicity + honesty**, not unsupported claims.
