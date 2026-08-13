from __future__ import annotations


def build_qbt_conditioner(model_dim: int, quantum_dim: int = 4):
    """Create a PyTorch projection + bounded gate module."""
    try:
        import torch
        from torch import nn
    except ImportError as exc:
        raise RuntimeError("Install qbt-bridge[torch] to use the PyTorch adapter.") from exc

    class QBTConditioner(nn.Module):
        def __init__(self):
            super().__init__()
            self.q_proj = nn.Linear(quantum_dim, model_dim)
            self.gate = nn.Linear(model_dim * 2, model_dim)
            self.norm = nn.LayerNorm(model_dim)

        def forward(self, hidden, q_vector):
            q = self.q_proj(q_vector)
            while q.dim() < hidden.dim():
                q = q.unsqueeze(1)
            q = q.expand_as(hidden)
            g = torch.sigmoid(self.gate(torch.cat([hidden, q], dim=-1)))
            return self.norm(hidden + g * q)

    return QBTConditioner()
