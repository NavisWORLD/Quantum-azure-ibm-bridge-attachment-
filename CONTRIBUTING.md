# Contributing

Thank you for your interest in Quantum Bridge Transformer (QBT).

## Contribution rights policy

This repository contains Cory-owned material that is now being developed under a restricted commercial rights strategy. External contributions are **not accepted for incorporation into proprietary Cory-owned material unless a written contribution, assignment, or other rights agreement is completed first**.

Opening an issue, discussion, or pull request does not transfer copyright ownership and does not by itself grant Cory Shane Davis / NavisWORLD a right to relicense your contribution.

If you want to contribute code or other copyrightable material, contact Cory Shane Davis / @NavisWORLD before submitting it so the applicable contribution terms can be agreed in writing.

## Research reports and factual feedback

Bug reports, reproducibility reports, benchmark results, security reports, documentation corrections, and citations are welcome. When reporting research results, include enough information to reproduce the result where practical: dataset snapshot, model/checkpoint, provider/backend, shots, seeds, control arms, software versions, and metrics.

Do not include code, datasets, model weights, confidential information, or other material you do not have the right to submit.

## Local verification

```bash
pip install -e ".[dev]"
pytest
ruff check src tests examples
```

## Provider reports should

1. label hardware/simulator/archive/fallback explicitly;
2. never disclose credentials;
3. preserve provider/backend/job provenance when available;
4. distinguish integration evidence from quantum-advantage claims;
5. include appropriate classical controls where a performance claim is made.

Null results are welcome. They are part of the evidence.

See `LICENSE`, `LICENSE_HISTORY.md`, and `COMMERCIAL_RIGHTS.md` before using or contributing material.
