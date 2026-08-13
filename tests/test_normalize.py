from qbt_bridge.models import ExecutionMode, QuantumSample
from qbt_bridge.normalize import blend_quantum_entropy, entropy_from_counts, normalize_sample


def test_entropy_extremes():
    assert entropy_from_counts({"0": 100}) == 0.0
    assert entropy_from_counts({"0": 50, "1": 50}) == 1.0


def test_normalize_and_blend():
    a = normalize_sample(
        QuantumSample(
            provider="a",
            backend="b",
            mode=ExecutionMode.HARDWARE,
            counts={"0": 50, "1": 50},
            shots=100,
        )
    )
    b = normalize_sample(
        QuantumSample(
            provider="c",
            backend="d",
            mode=ExecutionMode.HARDWARE,
            counts={"0": 90, "1": 10},
            shots=100,
        )
    )
    mix = blend_quantum_entropy([a, b])
    assert 0.0 <= mix <= 1.0
    assert a.result_digest
    assert len(a.normalized_vector) == 4


def test_blend_fallback():
    assert blend_quantum_entropy([], fallback=0.5) == 0.5
