# Bring Your Own Keys — Credential Setup

QBT is designed so every user, team, or company connects **their own** IBM Quantum and Azure Quantum accounts. No credential from the original COSMOS project is included or required.

## Fastest setup

```bash
cp .env.example .env
qbt configure
qbt doctor
```

`qbt configure` uses hidden terminal input for secret values and writes only to the local `.env` file. `.env` is gitignored. On operating systems that support POSIX file permissions, QBT attempts to set the file to owner-only (`0600`).

## IBM Quantum

Supported configuration:

```dotenv
IBM_QUANTUM_TOKEN=
IBM_QUANTUM_INSTANCE=
IBM_QUANTUM_BACKEND=
```

- `IBM_QUANTUM_TOKEN`: your IBM Quantum Platform API key.
- `IBM_QUANTUM_INSTANCE`: your service instance/CRN. Recommended by IBM because it avoids unnecessary instance discovery.
- `IBM_QUANTUM_BACKEND`: optional explicit QPU. Leave blank and the adapter attempts to choose an operational hardware backend.

QBT also supports a Qiskit Runtime account previously saved on the user's machine. In that mode, `IBM_QUANTUM_TOKEN` does not need to be written to this project at all.

Install:

```bash
pip install -e ".[ibm]"
```

Check local setup without printing the token:

```bash
qbt doctor
```

## Azure Quantum

Recommended workspace configuration:

```dotenv
AZURE_QUANTUM_RESOURCE_ID=
AZURE_QUANTUM_TARGET=
```

Alternative locator:

```dotenv
AZURE_SUBSCRIPTION_ID=
AZURE_QUANTUM_RESOURCE_GROUP=
AZURE_QUANTUM_WORKSPACE=
AZURE_QUANTUM_TARGET=
```

For Microsoft Entra service-principal authentication:

```dotenv
AZURE_TENANT_ID=
AZURE_CLIENT_ID=
AZURE_CLIENT_SECRET=
```

You can also authenticate using Azure CLI / `DefaultAzureCredential`, which avoids storing a client secret in the project.

Compatibility option:

```dotenv
AZURE_QUANTUM_CONNECTION_STRING=
```

Connection strings are supported for compatibility, but plaintext access keys are not the preferred production approach. Use Entra authorization/managed identity/secret management when possible.

Install:

```bash
pip install -e ".[azure]"
```

## Azure target runners

Azure Quantum has multiple hardware/software providers with different submission and result schemas. QBT intentionally does not pretend they all use one universal `run()` call.

Create a small runner for the provider you use:

```python
from qbt_bridge import QuantumBridge
from qbt_bridge.providers.azure import AzureQuantumProvider


def my_runner(workspace, target, shots):
    # Submit using the SDK/API for your selected Azure Quantum target.
    # Normalize the returned result into this minimum contract.
    return {
        "counts": {"0": 510, "1": 514},
        "job_id": "provider-job-id",
        "backend": target,
        "quality_class": "hardware",
    }


bridge = QuantumBridge([
    AzureQuantumProvider(runner=my_runner)
])
bridge.connect()
packet = bridge.control_packet(shots=1024)
```

This keeps the core QBT contract stable while allowing IonQ, Quantinuum, Microsoft/QDK targets, or future providers to change independently.

## Direct constructor injection

Environment variables are optional. Applications can inject credentials/configuration programmatically:

```python
provider = IBMQuantumProvider(
    token=my_secret_manager.get("ibm-quantum-token"),
    instance=my_secret_manager.get("ibm-instance"),
)
```

For production, this pattern with a proper secret manager is preferred over a local `.env` file.

## Secret-handling rules

QBT never intentionally includes tokens or connection strings in:

- normalized `QuantumState`
- prompt integration blocks
- result digests
- health/status output
- provenance metadata

Do not paste real keys into issues, pull requests, screenshots, demos, papers, or social-media posts.
