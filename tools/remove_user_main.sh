#!/usr/bin/env bash
set -euo pipefail
script_dir="$(cd "$(dirname "$0")" && pwd)"
port="${AI_PASSPORT_PORT:-$("$script_dir/find_port.sh")}"
python -m mpremote connect "$port" fs rm :main.py
echo "Removed /main.py from $port; the frozen example will run after reset."
