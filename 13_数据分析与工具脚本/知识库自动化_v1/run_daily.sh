#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VAULT="$(cd "$SCRIPT_DIR/../.." && pwd)"

exec /usr/bin/env python3 "$SCRIPT_DIR/run.py" run --vault "$VAULT"

