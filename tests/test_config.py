import os

from qbt_bridge.config import config_status, load_env_file, write_env_file


def test_env_round_trip(tmp_path, monkeypatch):
    path = tmp_path / ".env"
    write_env_file(
        {
            "IBM_QUANTUM_TOKEN": "secret-ibm-key-123",
            "IBM_QUANTUM_INSTANCE": "crn:test",
            "AZURE_QUANTUM_RESOURCE_ID": "/subscriptions/test/resourceGroups/rg/providers/Microsoft.Quantum/workspaces/qbt",
        },
        path,
        overwrite=True,
    )
    monkeypatch.delenv("IBM_QUANTUM_TOKEN", raising=False)
    monkeypatch.delenv("IBM_QUANTUM_INSTANCE", raising=False)
    monkeypatch.delenv("AZURE_QUANTUM_RESOURCE_ID", raising=False)
    load_env_file(path)
    assert os.environ["IBM_QUANTUM_TOKEN"] == "secret-ibm-key-123"
    assert os.environ["IBM_QUANTUM_INSTANCE"] == "crn:test"


def test_status_never_prints_secret(monkeypatch):
    monkeypatch.setenv("IBM_QUANTUM_TOKEN", "super-secret-token-abcdef")
    status = config_status(["IBM_QUANTUM_TOKEN"])
    assert "super-secret-token-abcdef" not in status["IBM_QUANTUM_TOKEN"]
    assert status["IBM_QUANTUM_TOKEN"] == "configured"
