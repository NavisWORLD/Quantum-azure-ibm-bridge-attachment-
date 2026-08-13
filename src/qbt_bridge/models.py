from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ExecutionMode(str, Enum):
    HARDWARE = "hardware"
    SIMULATOR = "simulator"
    ARCHIVE = "archive"
    FALLBACK = "fallback"


@dataclass(frozen=True)
class Quality:
    quality_class: str = "unknown"
    confidence: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class QuantumSample:
    provider: str
    backend: str
    mode: ExecutionMode
    counts: dict[str, int]
    shots: int
    job_id: str | None = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)
    quality: Quality = field(default_factory=Quality)

    def to_dict(self) -> dict[str, Any]:
        out = asdict(self)
        out["mode"] = self.mode.value
        return out


@dataclass(frozen=True)
class QuantumState:
    qbt_version: str
    provider: str
    backend: str
    execution_mode: str
    timestamp: str
    job_id: str | None
    shots: int
    entropy: float
    normalized_vector: tuple[float, ...]
    result_digest: str
    provenance: dict[str, Any]
    quality: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
