# Distribution and Adoption Guide

## License

The repository is distributed under the Apache License 2.0. This permits commercial use, modification, distribution, private use, and sublicensing subject to the license conditions, including preservation of required notices.

## Recommended downstream structure

A company integrating QBT should keep the bridge as a separate boundary package:

```text
application/
  model_or_agent/
  qbt_adapter/
  policy/
  telemetry/
```

Do not copy provider credentials into the package or bake them into container images.

## Vendoring

Organizations may vendor the source into a larger monorepo. Preserve:

- `LICENSE`
- `NOTICE`
- attribution to the original QBT work
- clear notices on modified files

## Forking

Forks should document changes to:

- normalization rules
- provider schemas
- fallback values
- neural gating
- provenance fields
- security/permission policies

Changing these can affect experimental comparability.

## Internal enterprise use

For internal deployment:

1. pin the QBT package/version or commit;
2. pin provider SDK versions;
3. store secrets in the organization's approved secret manager;
4. place QPU submission behind authorization and spending policy;
5. retain normalized provenance beside each downstream decision/inference;
6. validate the fail-soft path before production launch.

## Public research use

For reproducible papers/releases, publish:

- QBT commit SHA
- provider/backend and job IDs when publication is permitted
- shot counts
- circuit/program digest
- normalized state/result digest
- model and dataset hashes
- control-arm definition
- seeds
- metrics
- null results

## Citation

Use `CITATION.cff` for software citation. The foundational related CST deposit is:

**Cory Shane Davis, 12-Dimensional Cosmic Synapse Theory.**  
DOI: `10.5281/zenodo.17574447`

That DOI identifies related foundational work; it should not be represented as a DOI assigned specifically to this repository unless a separate deposit is created for this repository.
