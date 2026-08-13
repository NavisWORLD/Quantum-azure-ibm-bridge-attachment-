from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request

import pytest

from qbt_bridge.sidecar import make_server


def _request(url: str, *, body: dict | None = None, token: str | None = None) -> dict:
    data = None if body is None else json.dumps(body).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(request, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def _running_server(*, token: str | None = None):
    server = make_server("127.0.0.1", 0, auth_token=token)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def test_sidecar_health_sample_and_normalize():
    server, thread = _running_server()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        health = _request(f"{base}/health")
        assert health["status"] == "ok"
        assert health["credentials_exposed"] is False

        sample = _request(
            f"{base}/v1/sample",
            body={"provider": "simulator", "shots": 128, "seed": 7},
        )
        assert sample["packet"]["active_sources"] == 1
        assert sample["packet"]["provider_errors"] == {}

        normalized = _request(
            f"{base}/v1/normalize",
            body={
                "provider": "external",
                "backend": "unit-test",
                "mode": "simulator",
                "counts": {"0": 64, "1": 64},
                "shots": 128,
            },
        )
        assert normalized["state"]["entropy"] == pytest.approx(1.0)
        assert len(normalized["state"]["result_digest"]) == 64
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_network_bind_requires_token():
    with pytest.raises(ValueError, match="QBT_SIDECAR_TOKEN"):
        make_server("0.0.0.0", 0)


def test_bearer_token_protects_sidecar():
    server, thread = _running_server(token="test-token")
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        with pytest.raises(urllib.error.HTTPError) as exc:
            _request(f"{base}/health")
        assert exc.value.code == 401
        health = _request(f"{base}/health", token="test-token")
        assert health["status"] == "ok"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
