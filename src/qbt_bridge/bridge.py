from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .models import QuantumState
from .normalize import blend_quantum_entropy, normalize_sample
from .protocol import QuantumProvider


@dataclass
class QuantumBridge:
    """Provider-neutral bridge that normalizes quantum results for downstream AI/control."""

    providers: list[QuantumProvider]
    fallback: float = 0.5
    _last_states: list[QuantumState] = field(default_factory=list, init=False)
    _last_errors: dict[str, str] = field(default_factory=dict, init=False)

    def connect(self) -> dict[str, dict[str, Any]]:
        status: dict[str, dict[str, Any]] = {}
        for provider in self.providers:
            try:
                provider.connect()
                status[provider.name] = provider.health()
            except Exception as exc:  # noqa: BLE001 - fail-soft by design
                status[provider.name] = {
                    "available": False,
                    "active": False,
                    "error": str(exc),
                }
        return status

    def sample_all(self, *, shots: int = 1024) -> list[QuantumState]:
        states: list[QuantumState] = []
        self._last_errors = {}
        for provider in self.providers:
            try:
                sample = provider.sample(shots=shots)
                states.append(normalize_sample(sample))
            except Exception as exc:  # noqa: BLE001 - fail-soft by design
                self._last_errors[provider.name] = str(exc)
        self._last_states = states
        return list(states)

    def control_packet(self, *, shots: int = 1024) -> dict[str, Any]:
        states = self.sample_all(shots=shots)
        return {
            "qbt_version": "1.0",
            "active_sources": len(states),
            "quantum_mix": blend_quantum_entropy(states, fallback=self.fallback),
            "states": [s.to_dict() for s in states],
            "provider_errors": dict(self._last_errors),
        }

    def status(self) -> dict[str, Any]:
        provider_status: dict[str, Any] = {}
        for provider in self.providers:
            try:
                provider_status[provider.name] = provider.health()
            except Exception as exc:  # noqa: BLE001
                provider_status[provider.name] = {
                    "available": False,
                    "active": False,
                    "error": str(exc),
                }
        return {
            "qbt_version": "1.0",
            "providers": provider_status,
            "last_quantum_mix": blend_quantum_entropy(
                self._last_states, fallback=self.fallback
            ),
            "provider_errors": dict(self._last_errors),
        }

    def close(self) -> None:
        for provider in self.providers:
            try:
                provider.close()
            except Exception:  # noqa: BLE001,S110
                pass
