# Security Policy

## Supported version

The current development line is `0.2.x`.

## Reporting a vulnerability

Please use GitHub's private **Report a vulnerability / Security Advisory** flow when it is available for this repository. Do not publish credentials, exploit details, private account identifiers, provider tokens, connection strings, or sensitive logs in a public issue.

If a credential is accidentally exposed, revoke/rotate it with the relevant provider immediately before continuing investigation.

## Credential model

QBT is bring-your-own-account software. The repository contains no shared IBM Quantum or Azure Quantum credentials. Local `.env` files are gitignored, `qbt configure` hides secret input, and `qbt doctor` reports only whether secret fields are configured.

Production deployments should prefer organizational secret managers, Microsoft Entra/managed identity where appropriate, or provider-native saved-account mechanisms rather than committing local secret files.

## Scope

Security reports are especially useful for:

- credential leakage
- prompt/provenance secret exposure
- unsafe provider result parsing
- dependency or supply-chain issues
- bypasses of hardware/simulator labeling
- unbounded or malformed control vectors
