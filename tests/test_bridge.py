from qbt_bridge import QuantumBridge
from qbt_bridge.providers import SimulatorProvider


def test_bridge_packet():
    bridge = QuantumBridge([SimulatorProvider(seed=1)])
    status = bridge.connect()
    assert status["simulator"]["active"] is True

    packet = bridge.control_packet(shots=512)
    assert packet["qbt_version"] == "1.0"
    assert packet["active_sources"] == 1
    assert 0.0 <= packet["quantum_mix"] <= 1.0
    assert packet["states"][0]["execution_mode"] == "simulator"
