from __future__ import annotations

import argparse
import json

from .bridge import QuantumBridge
from .providers.simulator import SimulatorProvider


def main() -> None:
    parser = argparse.ArgumentParser(description="Quantum Bridge Transformer CLI")
    parser.add_argument("command", choices=["status", "sample"])
    parser.add_argument("--shots", type=int, default=1024)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    provider = SimulatorProvider(seed=args.seed)
    bridge = QuantumBridge([provider])
    bridge.connect()

    if args.command == "status":
        payload = bridge.status()
    else:
        payload = bridge.control_packet(shots=args.shots)

    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
