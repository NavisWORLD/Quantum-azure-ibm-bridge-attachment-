from __future__ import annotations

import random
import uuid
from typing import Any

from ..models import ExecutionMode, Quality, QuantumSample
from ..protocol import QuantumProvider


class SimulatorProvider(QuantumProvider):
    """Dependency-free classical control provider for development/null tests."""

    name = "simulator"

    def __init__(self, seed: int | None = None, backend: str = "python-prng-control"):
        self._rng = random.Random(seed)
        self.backend = backend
        self._connected = False

    def connect(self) -> None:
        self._connected = True

    def health(self) -> dict[str, Any]:
        return {
            "available": True,
            "active": self._connected,
            "provider": self.name,
            "backend": self.backend,
            "execution_mode": ExecutionMode.SIMULATOR.value,
        }

    def sample(self, *, shots: int = 1024) -> QuantumSample:
        if not self._connected:
            self.connect()
        counts = {"0": 0, "1": 0}
        for _ in range(shots):
            counts[str(self._rng.getrandbits(1))] += 1
        return QuantumSample(
            provider=self.name,
            backend=self.backend,
            mode=ExecutionMode.SIMULATOR,
            counts=counts,
            shots=shots,
            job_id=f"sim-{uuid.uuid4()}",
            quality=Quality("classical-control", 1.0),
            metadata={"warning": "Classical PRNG control; not quantum hardware."},
        )
