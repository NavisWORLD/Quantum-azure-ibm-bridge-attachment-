from __future__ import annotations

import json
import threading
import urllib.request

from qbt_bridge.sidecar import make_server


def request(url: str, body: dict | None = None) -> dict:
    data = None if body is None else json.dumps(body).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    server = make_server("127.0.0.1", 0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        assert request(f"{base}/health")["status"] == "ok"
        sample = request(
            f"{base}/v1/sample",
            {"provider": "simulator", "shots": 128, "seed": 7},
        )
        assert sample["packet"]["active_sources"] == 1
        normalized = request(
            f"{base}/v1/normalize",
            {
                "provider": "os-smoke",
                "backend": "local",
                "mode": "simulator",
                "counts": {"0": 64, "1": 64},
                "shots": 128,
            },
        )
        assert abs(normalized["state"]["entropy"] - 1.0) < 1e-12
        print("Cross-platform QBT sidecar smoke: OK")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


if __name__ == "__main__":
    main()
