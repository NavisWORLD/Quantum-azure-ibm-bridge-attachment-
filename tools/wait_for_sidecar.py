from __future__ import annotations

import sys
import time
import urllib.request


def main() -> None:
    url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8766/health"
    for _ in range(100):
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return
        except Exception:
            time.sleep(0.1)
    raise SystemExit(f"QBT sidecar did not become ready: {url}")


if __name__ == "__main__":
    main()
