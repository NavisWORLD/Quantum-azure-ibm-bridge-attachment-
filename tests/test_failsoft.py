from typing import Any

from qbt_bridge import QuantumBridge
from qbt_bridge.protocol import QuantumProvider


class BrokenProvider(QuantumProvider):
    name = "broken"

    def connect(self) -> None:
        raise RuntimeError("offline")

    def health(self) -> dict[str, Any]:
        raise RuntimeError("offline")

    def sample(self, *, shots: int = 1024):
        raise RuntimeError("offline")


def test_provider_failure_does_not_break_bridge():
    bridge = QuantumBridge([BrokenProvider()], fallback=0.5)
    status = bridge.connect()
    assert status["broken"]["active"] is False
    packet = bridge.control_packet()
    assert packet["active_sources"] == 0
    assert packet["quantum_mix"] == 0.5
