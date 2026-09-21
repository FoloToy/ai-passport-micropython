#!/usr/bin/env bash
set -euo pipefail
if [[ $# -ne 1 ]]; then
    echo "Usage: $0 path/to/main.py" >&2
    exit 2
fi
script_dir="$(cd "$(dirname "$0")" && pwd)"
file="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
port="${AI_PASSPORT_PORT:-$("$script_dir/find_port.sh")}"
python -m mpremote connect "$port" fs cp "$file" :main.py
echo "Uploaded $file to $port:/main.py"
