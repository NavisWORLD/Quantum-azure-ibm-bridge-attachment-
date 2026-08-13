from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Iterable
from typing import Any

from .models import QuantumSample, QuantumState


def _clip01(value: float) -> float:
    if not math.isfinite(value):
        return 0.5
    return max(0.0, min(1.0, value))


def entropy_from_counts(counts: dict[str, int]) -> float:
    """Return normalized Shannon entropy in [0, 1] for a counts dictionary."""
    if not counts:
        return 0.5
    total = sum(max(0, int(v)) for v in counts.values())
    if total <= 0:
        return 0.5
    positive = [v for v in counts.values() if v > 0]
    if len(positive) <= 1:
        return 0.0
    h = 0.0
    for value in positive:
        p = value / total
        h -= p * math.log2(p)
    h_max = math.log2(len(positive))
    return _clip01(h / h_max if h_max else 0.0)


def canonical_digest(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def normalize_sample(sample: QuantumSample) -> QuantumState:
    entropy = entropy_from_counts(sample.counts)
    source_flag = 1.0 if sample.mode.value == "hardware" else 0.0
    shot_reliability = _clip01(math.log2(max(sample.shots, 1)) / 16.0)
    confidence = (
        _clip01(float(sample.quality.confidence))
        if sample.quality.confidence is not None
        else 0.5
    )
    vector = (entropy, source_flag, shot_reliability, confidence)
    digest = canonical_digest({
        "provider": sample.provider,
        "backend": sample.backend,
        "mode": sample.mode.value,
        "counts": sample.counts,
        "shots": sample.shots,
        "job_id": sample.job_id,
        "timestamp": sample.timestamp,
    })
    return QuantumState(
        qbt_version="1.0",
        provider=sample.provider,
        backend=sample.backend,
        execution_mode=sample.mode.value,
        timestamp=sample.timestamp,
        job_id=sample.job_id,
        shots=sample.shots,
        entropy=entropy,
        normalized_vector=vector,
        result_digest=digest,
        provenance={
            "provider": sample.provider,
            "backend": sample.backend,
            "job_id": sample.job_id,
            "mode": sample.mode.value,
            "metadata": sample.metadata,
        },
        quality=sample.quality.to_dict(),
    )


def blend_quantum_entropy(
    states: Iterable[QuantumState | dict[str, Any]], *, fallback: float = 0.5
) -> float:
    """Average finite non-fallback entropy values and clip to [0, 1]."""
    values: list[float] = []
    for state in states:
        if isinstance(state, QuantumState):
            value = state.entropy
            mode = state.execution_mode
        elif isinstance(state, dict):
            value = state.get("entropy", state.get("last_entropy"))
            mode = state.get("execution_mode", state.get("mode"))
        else:
            continue
        if mode == "fallback":
            continue
        if isinstance(value, (int, float)) and math.isfinite(float(value)):
            values.append(float(value))
    if not values:
        return _clip01(fallback)
    return _clip01(sum(values) / len(values))
