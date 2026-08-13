from qbt_bridge import QuantumBridge
from qbt_bridge.integrations import to_prompt_block
from qbt_bridge.providers import SimulatorProvider

bridge = QuantumBridge([SimulatorProvider(seed=42)])
bridge.connect()

packet = bridge.control_packet(shots=1024)
prompt_control = to_prompt_block(packet)

user_prompt = "Generate three candidate search strategies."
full_prompt = f"{user_prompt}\n\n{prompt_control}"
print(full_prompt)
