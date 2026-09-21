#!/usr/bin/env bash
set -euo pipefail
script_dir="$(cd "$(dirname "$0")" && pwd)"
port="${AI_PASSPORT_PORT:-$("$script_dir/find_port.sh")}"
python -m mpremote connect "$port" exec "import sys; print('MicroPython:', sys.implementation); print('platform:', sys.platform)"
