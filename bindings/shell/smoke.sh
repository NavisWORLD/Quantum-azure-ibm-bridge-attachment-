#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-http://127.0.0.1:8766}"

curl --fail --silent --show-error "$BASE_URL/health" | grep -q '"status": "ok"\|"status":"ok"'

curl --fail --silent --show-error \
  -H 'Content-Type: application/json' \
  -d '{"provider":"simulator","shots":128,"seed":7}' \
  "$BASE_URL/v1/sample" | grep -q '"active_sources": 1\|"active_sources":1'

curl --fail --silent --show-error \
  -H 'Content-Type: application/json' \
  -d '{"provider":"shell","backend":"smoke","mode":"simulator","counts":{"0":64,"1":64},"shots":128}' \
  "$BASE_URL/v1/normalize" | grep -q '"entropy": 1.0\|"entropy":1.0'

echo 'Shell/curl QBT smoke: OK'
