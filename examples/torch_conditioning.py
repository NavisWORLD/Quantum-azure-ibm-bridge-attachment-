import torch

from qbt_bridge.integrations.torch import build_qbt_conditioner

batch, tokens, model_dim = 2, 8, 64
hidden = torch.randn(batch, tokens, model_dim)
q_vector = torch.tensor([[0.82, 1.0, 0.62, 0.5], [0.49, 0.0, 0.62, 1.0]])

conditioner = build_qbt_conditioner(model_dim=model_dim, quantum_dim=4)
conditioned = conditioner(hidden, q_vector)

print(hidden.shape, conditioned.shape)
