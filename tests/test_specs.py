from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_json_schemas_are_valid_json_and_versioned():
    state = json.loads((ROOT / "spec/qbt-state.schema.json").read_text(encoding="utf-8"))
    packet = json.loads(
        (ROOT / "spec/qbt-control-packet.schema.json").read_text(encoding="utf-8")
    )
    assert state["properties"]["qbt_version"]["const"] == "1.0"
    assert packet["properties"]["qbt_version"]["const"] == "1.0"
    assert packet["properties"]["states"]["items"]["$ref"] == "qbt-state.schema.json"


def test_openapi_declares_universal_endpoints():
    text = (ROOT / "spec/qbt-api.openapi.yaml").read_text(encoding="utf-8")
    assert "openapi: 3.1.0" in text
    for path in ("/health:", "/v1/status:", "/v1/sample:", "/v1/normalize:"):
        assert path in text
