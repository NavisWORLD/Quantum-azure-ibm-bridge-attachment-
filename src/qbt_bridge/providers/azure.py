from __future__ import annotations

import os
from typing import Any

from ..config import load_env_file
from ..models import ExecutionMode, Quality, QuantumSample
from ..protocol import QuantumProvider


class AzureQuantumProvider(QuantumProvider):
    """Azure Quantum workspace adapter with injected provider-specific execution.

    Workspace authentication follows Azure's normal credential chain. Users may
    authenticate with Azure CLI, Microsoft Entra service-principal environment
    variables, a resource ID, or (for compatibility) a connection string.
    """

    name = "azure"

    def __init__(
        self,
        *,
        workspace=None,
        runner=None,
        target: str | None = None,
        resource_group: str | None = None,
        workspace_name: str | None = None,
        subscription_id: str | None = None,
        resource_id: str | None = None,
        connection_string: str | None = None,
    ):
        load_env_file()
        self.workspace = workspace
        self.runner = runner
        self.target = target or os.getenv("AZURE_QUANTUM_TARGET")
        self.resource_group = resource_group or os.getenv("AZURE_QUANTUM_RESOURCE_GROUP")
        self.workspace_name = workspace_name or os.getenv("AZURE_QUANTUM_WORKSPACE")
        self.subscription_id = subscription_id or os.getenv("AZURE_SUBSCRIPTION_ID")
        self.resource_id = resource_id or os.getenv("AZURE_QUANTUM_RESOURCE_ID")
        self.connection_string = connection_string or os.getenv("AZURE_QUANTUM_CONNECTION_STRING")
        self._workspace_sdk = None

    @staticmethod
    def _workspace_class():
        try:
            from qdk.azure import Workspace

            return Workspace, "qdk.azure"
        except ImportError:
            try:
                from azure.quantum import Workspace

                return Workspace, "azure.quantum"
            except ImportError as exc:
                raise RuntimeError("Install qbt-bridge[azure] to use Azure Quantum.") from exc

    def connect(self) -> None:
        if self.workspace is not None:
            return
        Workspace, sdk_name = self._workspace_class()
        self._workspace_sdk = sdk_name

        if self.connection_string and hasattr(Workspace, "from_connection_string"):
            self.workspace = Workspace.from_connection_string(self.connection_string)
            return
        if self.resource_id:
            self.workspace = Workspace(resource_id=self.resource_id)
            return
        if self.subscription_id and self.resource_group and self.workspace_name:
            self.workspace = Workspace(
                subscription_id=self.subscription_id,
                resource_group=self.resource_group,
                name=self.workspace_name,
            )
            return
        if self.workspace_name:
            self.workspace = Workspace(name=self.workspace_name)
            return
        raise RuntimeError(
            "Azure workspace is not configured. Set AZURE_QUANTUM_RESOURCE_ID (recommended), "
            "or AZURE_SUBSCRIPTION_ID + AZURE_QUANTUM_RESOURCE_GROUP + AZURE_QUANTUM_WORKSPACE. "
            "Authenticate with Azure CLI/DefaultAzureCredential or AZURE_TENANT_ID + "
            "AZURE_CLIENT_ID + AZURE_CLIENT_SECRET."
        )

    def health(self) -> dict[str, Any]:
        return {
            "available": self.workspace is not None,
            "active": self.workspace is not None and self.runner is not None,
            "provider": self.name,
            "target": self.target,
            "workspace": self.workspace_name,
            "resource_id_configured": bool(self.resource_id),
            "execution_mode": ExecutionMode.HARDWARE.value,
            "workspace_sdk": self._workspace_sdk,
            "runner_configured": self.runner is not None,
            "note": "Sampling requires a provider-specific runner for the selected Azure target.",
        }

    def sample(self, *, shots: int = 1024) -> QuantumSample:
        if self.workspace is None:
            self.connect()
        if self.runner is None:
            raise RuntimeError(
                "AzureQuantumProvider requires runner(workspace, target, shots) -> dict "
                "because Azure provider targets have different job/result schemas."
            )
        result = self.runner(self.workspace, self.target, shots)
        if not isinstance(result, dict) or "counts" not in result:
            raise RuntimeError("Azure runner must return {'counts': {...}, ...}.")
        counts = {str(k): int(v) for k, v in result["counts"].items()}
        return QuantumSample(
            provider=self.name,
            backend=result.get("backend") or self.target or "azure-target",
            mode=ExecutionMode.HARDWARE,
            counts=counts,
            shots=sum(counts.values()),
            job_id=result.get("job_id"),
            quality=Quality(
                result.get("quality_class", "hardware"),
                result.get("confidence"),
            ),
            metadata={
                k: v
                for k, v in result.items()
                if k not in {"counts", "credential", "token", "secret", "connection_string"}
            },
        )
