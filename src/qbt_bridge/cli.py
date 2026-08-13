from __future__ import annotations

import argparse
import getpass
import json
import os

from .bridge import QuantumBridge
from .config import CONFIG_KEYS, config_status, load_env_file, missing_for, write_env_file
from .providers.simulator import SimulatorProvider


def _ask(label: str, *, secret: bool = False, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    prompt = f"{label}{suffix}: "
    value = getpass.getpass(prompt) if secret else input(prompt)
    return value.strip() or default


def configure(env_path: str, *, overwrite: bool = False) -> None:
    print("QBT credential wizard. Values are stored only in your local gitignored .env file.")
    print("Press Enter to skip any field. Existing non-empty values are preserved by default.")
    provider = _ask("Configure provider (ibm/azure/both)", default="both").lower()
    values: dict[str, str] = {}

    if provider in {"ibm", "both"}:
        values["IBM_QUANTUM_TOKEN"] = _ask("IBM Quantum API key", secret=True)
        values["IBM_QUANTUM_INSTANCE"] = _ask("IBM instance/CRN (recommended)")
        values["IBM_QUANTUM_BACKEND"] = _ask("IBM backend (optional; blank = least busy)")

    if provider in {"azure", "both"}:
        print("\nAzure: resource ID + Azure CLI/Entra auth is recommended.")
        values["AZURE_QUANTUM_RESOURCE_ID"] = _ask("Azure Quantum workspace resource ID")
        values["AZURE_SUBSCRIPTION_ID"] = _ask(
            "Azure subscription ID (alternative to resource ID)"
        )
        values["AZURE_QUANTUM_RESOURCE_GROUP"] = _ask("Azure resource group")
        values["AZURE_QUANTUM_WORKSPACE"] = _ask("Azure Quantum workspace name")
        values["AZURE_QUANTUM_TARGET"] = _ask("Azure Quantum target/provider name")
        values["AZURE_TENANT_ID"] = _ask("Azure tenant ID (service principal; optional)")
        values["AZURE_CLIENT_ID"] = _ask("Azure client ID (service principal; optional)")
        values["AZURE_CLIENT_SECRET"] = _ask(
            "Azure client secret (service principal; optional)", secret=True
        )

    path = write_env_file(values, env_path, overwrite=overwrite)
    print(f"Saved local configuration to {path}. This file is gitignored.")
    print("Run `qbt doctor` next. Secrets will never be printed by the doctor command.")


def doctor() -> None:
    loaded = load_env_file()
    print(f"QBT env file: {loaded or 'not found (using process environment/saved accounts)'}")
    statuses = config_status(CONFIG_KEYS)
    for key, status in statuses.items():
        print(f"{key:36} {status}")
    print("\nProvider readiness:")
    for provider in ("ibm", "azure"):
        missing = missing_for(provider)
        if missing:
            print(f"- {provider}: needs " + ", ".join(missing))
        else:
            print(f"- {provider}: configuration identifiers present")
    print("\nNote: `doctor` validates local configuration presence, not account permissions or QPU availability.")


def _provider(name: str, seed: int):
    if name == "simulator":
        return SimulatorProvider(seed=seed)
    if name == "ibm":
        from .providers.ibm import IBMQuantumProvider

        return IBMQuantumProvider()
    if name == "azure":
        from .providers.azure import AzureQuantumProvider

        return AzureQuantumProvider()
    raise ValueError(name)


def main() -> None:
    parser = argparse.ArgumentParser(description="Quantum Bridge Transformer CLI")
    parser.add_argument(
        "command",
        choices=["status", "sample", "configure", "doctor", "serve"],
    )
    parser.add_argument("--provider", choices=["simulator", "ibm", "azure"], default="simulator")
    parser.add_argument("--shots", type=int, default=1024)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--env-file", default=os.getenv("QBT_ENV_FILE", ".env"))
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing configured values during setup",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Sidecar bind host")
    parser.add_argument("--port", type=int, default=8766, help="Sidecar bind port")
    args = parser.parse_args()

    if args.command == "configure":
        configure(args.env_file, overwrite=args.overwrite)
        return
    if args.command == "doctor":
        doctor()
        return
    if args.command == "serve":
        from .sidecar import serve

        serve(args.host, args.port)
        return

    provider = _provider(args.provider, args.seed)
    bridge = QuantumBridge([provider])
    connection = bridge.connect()
    if args.command == "status":
        payload = {"connection": connection, "bridge": bridge.status()}
    else:
        packet = bridge.control_packet(shots=args.shots)
        payload = {"connection": connection, "packet": packet}
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
