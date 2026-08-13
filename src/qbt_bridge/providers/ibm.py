from __future__ import annotations

import os
from typing import Any

from ..config import load_env_file
from ..models import ExecutionMode, Quality, QuantumSample
from ..protocol import QuantumProvider


class IBMQuantumProvider(QuantumProvider):
    """IBM Quantum adapter using Qiskit Runtime Sampler V2.

    Credentials may be passed explicitly, loaded from a local gitignored `.env`,
    supplied through process environment variables, or resolved from a Qiskit
    Runtime account previously saved by the user.
    """

    name = "ibm"

    def __init__(
        self,
        *,
        token: str | None = None,
        backend: str | None = None,
        channel: str = "ibm_quantum_platform",
        instance: str | None = None,
    ):
        load_env_file()
        self.token = token or os.getenv("IBM_QUANTUM_TOKEN")
        self.backend_name = backend or os.getenv("IBM_QUANTUM_BACKEND")
        self.channel = channel
        self.instance = instance or os.getenv("IBM_QUANTUM_INSTANCE")
        self._service = None
        self._backend = None

    def connect(self) -> None:
        try:
            from qiskit_ibm_runtime import QiskitRuntimeService
        except ImportError as exc:
            raise RuntimeError("Install qbt-bridge[ibm] to use IBM Quantum.") from exc

        kwargs: dict[str, Any] = {"channel": self.channel}
        if self.token:
            kwargs["token"] = self.token
        if self.instance:
            kwargs["instance"] = self.instance
        try:
            self._service = QiskitRuntimeService(**kwargs)
        except Exception as exc:
            raise RuntimeError(
                "IBM authentication failed. Set IBM_QUANTUM_TOKEN (and preferably "
                "IBM_QUANTUM_INSTANCE) or save a default Qiskit Runtime account."
            ) from exc

        if self.backend_name:
            self._backend = self._service.backend(self.backend_name)
        else:
            try:
                self._backend = self._service.least_busy(operational=True, simulator=False)
            except Exception:
                candidates = list(self._service.backends(simulator=False, operational=True))
                if not candidates:
                    raise RuntimeError("No operational IBM hardware backend is available to this account.")
                self._backend = candidates[0]
            self.backend_name = getattr(self._backend, "name", None) or str(self._backend)

    def health(self) -> dict[str, Any]:
        return {
            "available": self._service is not None,
            "active": self._backend is not None,
            "provider": self.name,
            "backend": self.backend_name,
            "execution_mode": ExecutionMode.HARDWARE.value,
            "channel": self.channel,
            "instance_configured": bool(self.instance),
            "credential_source": "explicit/env" if self.token else "saved-account/default",
        }

    def sample(self, *, shots: int = 1024) -> QuantumSample:
        if self._backend is None:
            self.connect()
        try:
            from qiskit import QuantumCircuit, transpile
            from qiskit_ibm_runtime import SamplerV2
        except ImportError as exc:
            raise RuntimeError("Install qbt-bridge[ibm] to use IBM Quantum.") from exc

        qc = QuantumCircuit(1)
        qc.h(0)
        qc.measure_all()
        tqc = transpile(qc, self._backend, optimization_level=1)

        sampler = SamplerV2(mode=self._backend)
        job = sampler.run([tqc], shots=shots)
        pub_result = job.result()[0]
        raw_counts = pub_result.data.meas.get_counts()
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
                "primitive": "SamplerV2",
                "provider_contract": "qbt-1.0",
            },
        )
