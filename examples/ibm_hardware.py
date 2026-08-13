from qbt_bridge import QuantumBridge
from qbt_bridge.providers.ibm import IBMQuantumProvider

# Configure via `qbt configure`, environment variables, or a saved Qiskit Runtime account.
provider = IBMQuantumProvider()
bridge = QuantumBridge([provider])
print(bridge.connect())
print(bridge.control_packet(shots=1024))
