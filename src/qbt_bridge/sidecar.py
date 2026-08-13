from __future__ import annotations

import hmac
import json
import os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from ipaddress import ip_address
from typing import Any
from urllib.parse import parse_qs, urlparse

from .bridge import QuantumBridge
from .models import ExecutionMode, Quality, QuantumSample
from .normalize import normalize_sample
from .providers.simulator import SimulatorProvider

MAX_BODY_BYTES = 1_048_576
MAX_SHOTS = 1_000_000
LIVE_PROVIDERS = frozenset({"ibm", "azure"})


def _provider(name: str, seed: int):
    if name == "simulator":
        return SimulatorProvider(seed=seed)
    if name == "ibm":
        from .providers.ibm import IBMQuantumProvider

        return IBMQuantumProvider()
    if name == "azure":
        from .providers.azure import AzureQuantumProvider

        return AzureQuantumProvider()
    raise ValueError(f"unsupported provider: {name}")


def _validated_shots(value: Any) -> int:
    shots = int(value)
    if shots < 1 or shots > MAX_SHOTS:
        raise ValueError(f"shots must be between 1 and {MAX_SHOTS}")
    return shots


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def sample_payload(
    provider: str = "simulator", shots: int = 1024, seed: int = 42
) -> dict[str, Any]:
    bridge = QuantumBridge([_provider(provider, int(seed))])
    connection = bridge.connect()
    packet = bridge.control_packet(shots=_validated_shots(shots))
    return {"connection": connection, "packet": packet}


def status_payload(provider: str = "simulator", seed: int = 42) -> dict[str, Any]:
    bridge = QuantumBridge([_provider(provider, int(seed))])
    connection = bridge.connect()
    return {"connection": connection, "bridge": bridge.status()}


def normalize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    raw_counts = payload.get("counts")
    if not isinstance(raw_counts, dict) or not raw_counts:
        raise ValueError("counts must be a non-empty object")

    counts: dict[str, int] = {}
    for key, value in raw_counts.items():
        count = int(value)
        if count < 0:
            raise ValueError("counts must be non-negative")
        counts[str(key)] = count

    shots = _validated_shots(payload.get("shots", sum(counts.values())))
    mode = ExecutionMode(str(payload.get("mode", "simulator")))
    confidence = payload.get("confidence")
    quality = Quality(
        quality_class=str(payload.get("quality_class", "external")),
        confidence=None if confidence is None else float(confidence),
    )
    sample = QuantumSample(
        provider=str(payload.get("provider", "external")),
        backend=str(payload.get("backend", "external")),
        mode=mode,
        counts=counts,
        shots=shots,
        job_id=payload.get("job_id"),
        timestamp=str(payload.get("timestamp") or datetime.now(timezone.utc).isoformat()),
        metadata=payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {},
        quality=quality,
    )
    return {"state": normalize_sample(sample).to_dict()}


def _is_loopback(host: str) -> bool:
    if host.lower() == "localhost":
        return True
    try:
        return ip_address(host).is_loopback
    except ValueError:
        return False


class QbtHttpServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(
        self,
        server_address: tuple[str, int],
        handler_class: type[BaseHTTPRequestHandler],
        *,
        auth_token: str | None = None,
        allow_origin: str | None = None,
        allow_live_providers: bool = False,
    ) -> None:
        super().__init__(server_address, handler_class)
        self.auth_token = auth_token or None
        self.allow_origin = allow_origin or None
        self.allow_live_providers = bool(allow_live_providers)


class QbtRequestHandler(BaseHTTPRequestHandler):
    server: QbtHttpServer
    server_version = "QBT-Sidecar/1.0"

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _headers(self) -> None:
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        if self.server.allow_origin:
            self.send_header("Access-Control-Allow-Origin", self.server.allow_origin)
            self.send_header("Vary", "Origin")

    def _send(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
        self.send_response(status)
        self._headers()
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _authorized(self) -> bool:
        token = self.server.auth_token
        if not token:
            return True
        supplied = self.headers.get("Authorization", "")
        return hmac.compare_digest(supplied, f"Bearer {token}")

    def _require_auth(self) -> bool:
        if self._authorized():
            return True
        self._send(401, {"error": "unauthorized"})
        return False

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length < 0 or length > MAX_BODY_BYTES:
            raise ValueError("request body is too large")
        raw = self.rfile.read(length)
        if not raw:
            return {}
        payload = json.loads(raw.decode("utf-8"))
        if not isinstance(payload, dict):
            raise TypeError("JSON body must be an object")
        return payload

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self._headers()
        self.send_header("Access-Control-Allow-Headers", "authorization, content-type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_GET(self) -> None:
        if not self._require_auth():
            return
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        try:
            if parsed.path == "/health":
                self._send(
                    200,
                    {
                        "service": "qbt-sidecar",
                        "status": "ok",
                        "qbt_version": "1.0",
                        "credentials_exposed": False,
                        "live_provider_execution": self.server.allow_live_providers,
                    },
                )
                return
            if parsed.path == "/v1/status":
                provider = query.get("provider", ["simulator"])[0]
                seed = int(query.get("seed", ["42"])[0])
                self._send(200, status_payload(provider=provider, seed=seed))
                return
            self._send(404, {"error": "not found"})
        except (TypeError, ValueError) as exc:
            self._send(400, {"error": str(exc)})
        except Exception as exc:  # noqa: BLE001 - provider boundary returns structured JSON
            self._send(502, {"error": f"provider failure: {exc}"})

    def do_POST(self) -> None:
        if not self._require_auth():
            return
        parsed = urlparse(self.path)
        try:
            payload = self._read_json()
            if parsed.path == "/v1/sample":
                provider = str(payload.get("provider", "simulator"))
                if provider in LIVE_PROVIDERS and not self.server.allow_live_providers:
                    self._send(
                        403,
                        {
                            "error": (
                                "live provider execution is disabled; restart QBT with "
                                "--allow-live-providers or set QBT_ALLOW_LIVE_PROVIDERS=1"
                            )
                        },
                    )
                    return
                self._send(
                    200,
                    sample_payload(
                        provider=provider,
                        shots=_validated_shots(payload.get("shots", 1024)),
                        seed=int(payload.get("seed", 42)),
                    ),
                )
                return
            if parsed.path == "/v1/normalize":
                self._send(200, normalize_payload(payload))
                return
            self._send(404, {"error": "not found"})
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            self._send(400, {"error": str(exc)})
        except Exception as exc:  # noqa: BLE001 - provider boundary returns structured JSON
            self._send(502, {"error": f"provider failure: {exc}"})


def make_server(
    host: str = "127.0.0.1",
    port: int = 8766,
    *,
    auth_token: str | None = None,
    allow_origin: str | None = None,
    allow_live_providers: bool | None = None,
) -> QbtHttpServer:
    token = auth_token or os.getenv("QBT_SIDECAR_TOKEN") or None
    origin = allow_origin or os.getenv("QBT_ALLOW_ORIGIN") or None
    live = (
        _truthy(os.getenv("QBT_ALLOW_LIVE_PROVIDERS"))
        if allow_live_providers is None
        else bool(allow_live_providers)
    )
    if not _is_loopback(host) and not token:
        raise ValueError(
            "refusing non-loopback bind without QBT_SIDECAR_TOKEN; "
            "set a bearer token before exposing QBT on a network"
        )
    return QbtHttpServer(
        (host, int(port)),
        QbtRequestHandler,
        auth_token=token,
        allow_origin=origin,
        allow_live_providers=live,
    )


def serve(
    host: str = "127.0.0.1",
    port: int = 8766,
    *,
    allow_live_providers: bool | None = None,
) -> None:
    server = make_server(host, port, allow_live_providers=allow_live_providers)
    print(f"QBT sidecar listening on http://{host}:{server.server_port}")
    print("No provider credentials are exposed by the HTTP API.")
    print(f"Live provider execution: {'enabled' if server.allow_live_providers else 'disabled'}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
