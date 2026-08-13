"""Quantum Bridge Transformer (QBT) integration toolkit."""

from .bridge import QuantumBridge
from .models import ExecutionMode, Quality, QuantumSample, QuantumState
from .normalize import blend_quantum_entropy, entropy_from_counts

__all__ = [
    "ExecutionMode",
    "Quality",
    "QuantumBridge",
    "QuantumSample",
    "QuantumState",
    "blend_quantum_entropy",
    "entropy_from_counts",
]

__version__ = "0.3.0"
