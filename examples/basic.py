from qbt_bridge import QuantumBridge
from qbt_bridge.providers import SimulatorProvider

bridge = QuantumBridge([SimulatorProvider(seed=7)])
print(bridge.connect())
packet = bridge.control_packet(shots=2048)
print(packet["quantum_mix"])
print(packet["states"][0]["provenance"])
