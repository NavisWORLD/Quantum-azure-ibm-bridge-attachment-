from __future__ import annotations

import os
from typing import Any

from ..models import ExecutionMode, Quality, QuantumSample
from ..protocol import QuantumProvider


class AzureQuantumProvider(QuantumProvider):
    """Azure Quantum adapter with an injected provider-specific runner."""

    name = "azure"

    def __init__(
        self,
        *,
        workspace=None,
        runner=None,
        target: str | None = None,
        resource_group: str | None = None,
        workspace_name: str | None = None,
        location: str | None = None,
        subscription_id: str | None = None,
    ):
        self.workspace = workspace
        self.runner = runner
        self.target = target or os.getenv("AZURE_QUANTUM_TARGET")
        self.resource_group = resource_group or os.getenv("AZURE_QUANTUM_RESOURCE_GROUP")
        self.workspace_name = workspace_name or os.getenv("AZURE_QUANTUM_WORKSPACE")
        self.location = location or os.getenv("AZURE_QUANTUM_LOCATION")
        self.subscription_id = subscription_id or os.getenv("AZURE_SUBSCRIPTION_ID")

    def connect(self) -> None:
        if self.workspace is not None:
            return
        try:
            from azure.quantum import Workspace
        except ImportError as exc:
            raise RuntimeError("Install qbt-bridge[azure] to use Azure Quantum.") from exc

        required = {
            "subscription_id": self.subscription_id,
            "resource_group": self.resource_group,
            "name": self.workspace_name,
            "location": self.location,
        }
        missing = [k for k, v in required.items() if not v]
        if missing:
            raise RuntimeError("Missing Azure Quantum configuration: " + ", ".join(missing))
        self.workspace = Workspace(**required)

    def health(self) -> dict[str, Any]:
        return {
            "available": self.workspace is not None,
            "active": self.workspace is not None and self.runner is not None,
            "provider": self.name,
            "target": self.target,
            "workspace": self.workspace_name,
            "location": self.location,
            "execution_mode": ExecutionMode.HARDWARE.value,
            "note": "A provider-specific runner must be supplied for sampling.",
        }

    def sample(self, *, shots: int = 1024) -> QuantumSample:
        if self.workspace is None:
            self.connect()
        if self.runner is None:
            raise RuntimeError(
                "AzureQuantumProvider requires runner(workspace, target, shots) -> dict."
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
                if k not in {"counts", "credential", "token", "secret"}
            },
        )
