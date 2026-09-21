#!/usr/bin/env bash
set -euo pipefail
if [[ $# -ne 1 ]]; then
    echo "Usage: $0 path/to/merged.bin" >&2
    exit 2
fi
script_dir="$(cd "$(dirname "$0")" && pwd)"
port="${AI_PASSPORT_PORT:-$("$script_dir/find_port.sh")}"
image="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
python -m esptool --chip esp32c3 --port "$port" write_flash 0x0 "$image"
