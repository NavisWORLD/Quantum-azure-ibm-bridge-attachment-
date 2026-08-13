from __future__ import annotations

import os
from typing import Any

from ..models import ExecutionMode, Quality, QuantumSample
from ..protocol import QuantumProvider


class IBMQuantumProvider(QuantumProvider):
    """IBM Quantum adapter with server-side credential handling."""

    name = "ibm"

    def __init__(
        self,
        *,
        token: str | None = None,
        backend: str | None = None,
        channel: str = "ibm_quantum_platform",
        instance: str | None = None,
    ):
        self.token = token or os.getenv("IBM_QUANTUM_TOKEN")
        self.backend_name = backend or os.getenv("IBM_QUANTUM_BACKEND")
        self.channel = channel
        self.instance = instance or os.getenv("IBM_QUANTUM_INSTANCE")
        self._service = None
        self._backend = None

    def connect(self) -> None:
        if not self.token:
            raise RuntimeError("IBM_QUANTUM_TOKEN is not configured.")
        try:
            from qiskit_ibm_runtime import QiskitRuntimeService
        except ImportError as exc:
            raise RuntimeError("Install qbt-bridge[ibm] to use IBM Quantum.") from exc

        kwargs: dict[str, Any] = {"channel": self.channel, "token": self.token}
        if self.instance:
            kwargs["instance"] = self.instance
        self._service = QiskitRuntimeService(**kwargs)

        if self.backend_name:
            self._backend = self._service.backend(self.backend_name)
        else:
            candidates = list(self._service.backends(simulator=False, operational=True))
            if not candidates:
                raise RuntimeError("No operational IBM hardware backend available.")
            self._backend = candidates[0]
            self.backend_name = getattr(self._backend, "name", None) or str(self._backend)

    def health(self) -> dict[str, Any]:
        return {
            "available": self._service is not None,
            "active": self._backend is not None,
            "provider": self.name,
            "backend": self.backend_name,
            "execution_mode": ExecutionMode.HARDWARE.value,
        }

    def sample(self, *, shots: int = 1024) -> QuantumSample:
        if self._backend is None:
            self.connect()
        try:
            from qiskit import QuantumCircuit, transpile
        except ImportError as exc:
            raise RuntimeError("Install qbt-bridge[ibm] to use IBM Quantum.") from exc

        qc = QuantumCircuit(1, 1)
        qc.h(0)
        qc.measure(0, 0)
        tqc = transpile(qc, self._backend)
        job = self._backend.run(tqc, shots=shots)
        result = job.result()
        raw_counts = result.get_counts()
        counts = {str(k).replace(" ", ""): int(v) for k, v in raw_counts.items()}

        return QuantumSample(
            provider=self.name,
            backend=self.backend_name or "unknown",
            mode=ExecutionMode.HARDWARE,
            counts=counts,
            shots=sum(counts.values()),
            job_id=job.job_id(),
            quality=Quality("hardware", None),
            metadata={
                "circuit": "1q-hadamard-measurement",
                "provider_contract": "qbt-1.0",
            },
        )
