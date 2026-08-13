from __future__ import annotations

import json
from typing import Any


def to_prompt_block(control_packet: dict[str, Any]) -> str:
    """Serialize non-secret bounded bridge state for prompt-level integration."""
    safe = {
        "qbt_version": control_packet.get("qbt_version"),
        "active_sources": control_packet.get("active_sources", 0),
        "quantum_mix": control_packet.get("quantum_mix", 0.5),
        "sources": [
            {
                "provider": s.get("provider"),
                "backend": s.get("backend"),
                "execution_mode": s.get("execution_mode"),
                "entropy": s.get("entropy"),
                "shots": s.get("shots"),
                "result_digest": s.get("result_digest"),
            }
            for s in control_packet.get("states", [])
        ],
    }
    return "[QBT_CONTROL]\n" + json.dumps(safe, sort_keys=True) + "\n[/QBT_CONTROL]"
