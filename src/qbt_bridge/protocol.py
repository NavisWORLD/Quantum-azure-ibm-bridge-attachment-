from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .models import QuantumSample


class QuantumProvider(ABC):
    """Minimal provider contract used by QuantumBridge."""

    name: str

    @abstractmethod
    def connect(self) -> None:
        """Initialize provider resources or validate configuration."""

    @abstractmethod
    def health(self) -> dict[str, Any]:
        """Return non-secret provider status."""

    @abstractmethod
    def sample(self, *, shots: int = 1024) -> QuantumSample:
        """Return one measured/simulated sample."""

    def close(self) -> None:
        """Optional cleanup hook."""
