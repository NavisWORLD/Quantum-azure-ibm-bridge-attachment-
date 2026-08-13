# Security, Privacy, and Production Safety

## Credentials

Never store provider credentials in:

- Git
- browser JavaScript
- prompts
- telemetry packets
- experiment artifacts intended for public release

Use environment variables or a production secret manager.

## Permissions

Real hardware submissions should pass a policy gate that can enforce:

- user/service authorization
- spending limits
- allowed providers/targets
- maximum shots
- rate limits
- approval/MFA for high-cost runs

## Input validation

Treat provider results as untrusted external input. Validate:

- counts are integer and non-negative
- total shots are reasonable
- entropy is finite
- backend/job metadata is strings
- result sizes are bounded

## Fail-soft behavior

A QPU outage must not take down the host AI system. The default bridge implementation skips failed providers and returns a bounded fallback.

## Privacy

QBT does not require raw user audio, camera frames, biometrics, or conversation logs. If a host project combines QBT with those systems, that host project is responsible for consent, retention, minimization, and access control.

## Claim safety

Do not turn an integration signal into a physical or medical claim. QBT is an engineering interface.
