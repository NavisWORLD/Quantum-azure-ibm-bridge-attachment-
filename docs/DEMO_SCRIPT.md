# Two-Minute Demo Script

## 0:00–0:15 — Hook

"This is a detachable bridge between quantum-computing services and an ordinary AI project. You bring your own IBM or Azure account; the model stays yours."

## 0:15–0:35 — Configure

```bash
qbt configure
qbt doctor
```

Point out that secret values are masked and `.env` is gitignored.

## 0:35–0:55 — Zero-cost control

```bash
qbt sample --shots 1024
```

Explain that the default CLI sample is deliberately a classical simulator/control and is labeled as such.

## 0:55–1:20 — Hardware adapter

Show `IBMQuantumProvider()` or `AzureQuantumProvider(...)` and the resulting provider/backend/job ID/result digest. Do not reveal credentials.

## 1:20–1:40 — AI attachment

Show the normalized vector:

```text
[entropy, hardware_flag, shot_reliability, confidence]
```

Then show `build_qbt_conditioner(model_dim=...)`.

## 1:40–2:00 — Research discipline

End with:

```text
hardware | simulator | classical random | fixed | disabled
```

"The bridge is real. Whether the quantum channel improves a particular task is an experiment, not a slogan."
