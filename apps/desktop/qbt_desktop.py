from __future__ import annotations

import json
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
from urllib import error, request

from qbt_bridge import QuantumBridge
from qbt_bridge.providers.simulator import SimulatorProvider

APP_NAME = "QBT Desktop"
APP_VERSION = "0.4.0"
CONFIG_PATH = Path.home() / ".qbt" / "desktop.json"


def load_config() -> dict[str, str]:
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_config(payload: dict[str, str]) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def http_json(url: str, method: str = "GET", payload=None, token: str = ""):
    headers = {"Accept": "application/json"}
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = request.Request(url, data=data, headers=headers, method=method)
    with request.urlopen(req, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


class QBTDesktop(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} {APP_VERSION}")
        self.geometry("1000x700")
        self.minsize(820, 600)
        self.configure(bg="#08111d")
        self._configure_style()
        cfg = load_config()
        self.endpoint = tk.StringVar(value=cfg.get("endpoint", "http://127.0.0.1:8766"))
        self.token = tk.StringVar(value=cfg.get("token", ""))
        self.shots = tk.IntVar(value=1024)
        self.seed = tk.IntVar(value=42)
        self.counts = tk.StringVar(value="0=512,1=512")
        self.status_text = tk.StringVar(value="Ready")
        self._build()

    def _configure_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background="#08111d")
        style.configure("Card.TFrame", background="#101e30")
        style.configure("TLabel", background="#08111d", foreground="#d9e8ff", font=("Segoe UI", 11))
        style.configure("Hero.TLabel", background="#08111d", foreground="#f4fbff", font=("Segoe UI Semibold", 24))
        style.configure("Sub.TLabel", background="#08111d", foreground="#7fa8d8", font=("Segoe UI", 10))
        style.configure("Card.TLabel", background="#101e30", foreground="#d9e8ff", font=("Segoe UI", 11))
        style.configure("Accent.TButton", font=("Segoe UI Semibold", 10), padding=(16, 10))
        style.configure("TButton", font=("Segoe UI", 10), padding=(12, 8))
        style.configure("TEntry", fieldbackground="#13263d", foreground="#eef7ff", insertcolor="#eef7ff")
        style.configure("TNotebook", background="#08111d", borderwidth=0)
        style.configure("TNotebook.Tab", padding=(16, 9))

    def _build(self):
        header = ttk.Frame(self, padding=(24, 20, 24, 8))
        header.pack(fill="x")
        ttk.Label(header, text="Quantum Bridge Transformer", style="Hero.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="Local simulation, auditable normalization, and secure sidecar control in one desktop shell.",
            style="Sub.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=22, pady=14)
        notebook.add(self._sample_tab(notebook), text="Control")
        notebook.add(self._normalize_tab(notebook), text="Normalize")
        notebook.add(self._settings_tab(notebook), text="Connection")

        footer = ttk.Frame(self, padding=(22, 4, 22, 16))
        footer.pack(fill="x")
        ttk.Label(footer, textvariable=self.status_text, style="Sub.TLabel").pack(side="left")
        ttk.Label(footer, text=f"QBT {APP_VERSION} • BYOK • no credentials bundled", style="Sub.TLabel").pack(side="right")

    def _output_box(self, parent):
        box = tk.Text(parent, wrap="word", bg="#07101b", fg="#dff2ff", insertbackground="#dff2ff", relief="flat", font=("Consolas", 10))
        box.pack(fill="both", expand=True, pady=(12, 0))
        box.insert("1.0", "Run a control action to see a QBT packet here.\n")
        return box

    def _sample_tab(self, parent):
        frame = ttk.Frame(parent, padding=18)
        controls = ttk.Frame(frame, style="Card.TFrame", padding=16)
        controls.pack(fill="x")
        ttk.Label(controls, text="Shots", style="Card.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Entry(controls, textvariable=self.shots, width=10).grid(row=0, column=1, padx=(8, 18))
        ttk.Label(controls, text="Seed", style="Card.TLabel").grid(row=0, column=2, sticky="w")
        ttk.Entry(controls, textvariable=self.seed, width=10).grid(row=0, column=3, padx=(8, 18))
        ttk.Button(controls, text="Local simulator", style="Accent.TButton", command=self.local_sample).grid(row=0, column=4, padx=4)
        ttk.Button(controls, text="Sidecar sample", command=self.sidecar_sample).grid(row=0, column=5, padx=4)
        ttk.Button(controls, text="Health", command=self.health).grid(row=0, column=6, padx=4)
        self.sample_output = self._output_box(frame)
        return frame

    def _normalize_tab(self, parent):
        frame = ttk.Frame(parent, padding=18)
        controls = ttk.Frame(frame, style="Card.TFrame", padding=16)
        controls.pack(fill="x")
        ttk.Label(controls, text="Counts, e.g. 0=512,1=512", style="Card.TLabel").pack(side="left")
        ttk.Entry(controls, textvariable=self.counts, width=34).pack(side="left", padx=10)
        ttk.Button(controls, text="Normalize", style="Accent.TButton", command=self.normalize_remote).pack(side="left")
        self.normalize_output = self._output_box(frame)
        return frame

    def _settings_tab(self, parent):
        frame = ttk.Frame(parent, padding=18)
        card = ttk.Frame(frame, style="Card.TFrame", padding=20)
        card.pack(fill="x")
        ttk.Label(card, text="QBT sidecar URL", style="Card.TLabel").grid(row=0, column=0, sticky="w", pady=6)
        ttk.Entry(card, textvariable=self.endpoint, width=55).grid(row=0, column=1, sticky="ew", padx=12, pady=6)
        ttk.Label(card, text="Bearer token", style="Card.TLabel").grid(row=1, column=0, sticky="w", pady=6)
        ttk.Entry(card, textvariable=self.token, show="•", width=55).grid(row=1, column=1, sticky="ew", padx=12, pady=6)
        ttk.Button(card, text="Save connection", style="Accent.TButton", command=self.save_connection).grid(row=2, column=1, sticky="e", padx=12, pady=(12, 0))
        card.columnconfigure(1, weight=1)
        ttk.Label(
            frame,
            text=(
                "Use loopback for a sidecar on this computer. For mobile clients, expose QBT on your LAN or HTTPS endpoint "
                "and protect non-loopback binds with QBT_SIDECAR_TOKEN. Live IBM/Azure sidecar jobs remain opt-in."
            ),
            style="Sub.TLabel",
            wraplength=760,
            justify="left",
        ).pack(anchor="w", pady=18)
        return frame

    def _set_output(self, box: tk.Text, payload):
        box.delete("1.0", "end")
        box.insert("1.0", json.dumps(payload, indent=2, sort_keys=True))

    def _run(self, fn, box: tk.Text):
        self.status_text.set("Working…")

        def worker():
            try:
                result = fn()
                self.after(0, lambda: self._set_output(box, result))
                self.after(0, lambda: self.status_text.set("Success"))
            except error.HTTPError as exc:
                body = exc.read().decode("utf-8", "replace")
                self.after(0, lambda: self._set_output(box, {"error": f"HTTP {exc.code}", "body": body}))
                self.after(0, lambda: self.status_text.set("Request failed"))
            except Exception as exc:
                self.after(0, lambda: self._set_output(box, {"error": str(exc)}))
                self.after(0, lambda: self.status_text.set("Operation failed"))

        threading.Thread(target=worker, daemon=True).start()

    def local_sample(self):
        shots = max(1, min(int(self.shots.get()), 1_000_000))
        seed = int(self.seed.get())

        def action():
            bridge = QuantumBridge([SimulatorProvider(seed=seed)])
            bridge.connect()
            return bridge.control_packet(shots=shots)

        self._run(action, self.sample_output)

    def sidecar_sample(self):
        endpoint = self.endpoint.get().rstrip("/")
        payload = {"provider": "simulator", "shots": int(self.shots.get()), "seed": int(self.seed.get())}
        self._run(lambda: http_json(f"{endpoint}/v1/sample", "POST", payload, self.token.get()), self.sample_output)

    def health(self):
        endpoint = self.endpoint.get().rstrip("/")
        self._run(lambda: http_json(f"{endpoint}/health", token=self.token.get()), self.sample_output)

    def normalize_remote(self):
        counts: dict[str, int] = {}
        for pair in self.counts.get().split(","):
            key, value = pair.split("=", 1)
            counts[key.strip()] = int(value.strip())
        endpoint = self.endpoint.get().rstrip("/")
        payload = {"provider": "external", "backend": "desktop", "execution_mode": "archive", "counts": counts}
        self._run(lambda: http_json(f"{endpoint}/v1/normalize", "POST", payload, self.token.get()), self.normalize_output)

    def save_connection(self):
        save_config({"endpoint": self.endpoint.get().strip(), "token": self.token.get()})
        self.status_text.set(f"Saved connection settings to {CONFIG_PATH}")
        messagebox.showinfo(APP_NAME, "Connection settings saved locally.")


if __name__ == "__main__":
    QBTDesktop().mainloop()
