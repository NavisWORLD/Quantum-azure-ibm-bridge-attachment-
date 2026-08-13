# Contributing

Thank you for helping make QBT more useful and more falsifiable.

## Good contributions

- new provider adapters/runners
- reproducible hardware-vs-control benchmarks
- security improvements
- platform compatibility fixes
- examples for real host AI systems
- documentation corrections
- null results

## Before opening a PR

```bash
pip install -e ".[dev]"
pytest
ruff check src tests examples
```

## Provider contributions must

1. label hardware/simulator/archive/fallback explicitly;
2. never log credentials;
3. normalize into `QuantumSample` / `QuantumState`;
4. preserve provider/backend/job provenance when available;
5. fail without crashing unrelated host inference;
6. include tests that do not require paid hardware.

## Research contributions

Include enough information to reproduce the result: dataset snapshot, model/checkpoint, provider/backend, shots, seeds, control arms, software versions, and metrics.

Null results are welcome. They are part of the evidence, not failed contributions.
