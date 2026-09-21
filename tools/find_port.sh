#!/usr/bin/env bash
set -euo pipefail
if [[ -n "${AI_PASSPORT_PORT:-}" ]]; then
    printf '%s\n' "$AI_PASSPORT_PORT"
    exit 0
fi
for port in /dev/ttyACM* /dev/ttyUSB*; do
    if [[ -e "$port" ]]; then
        printf '%s\n' "$port"
        exit 0
    fi
done
cat >&2 <<'EOF'
No AI Passport serial port was found.
Power on the board and connect it with a data-capable USB cable, then try again.
EOF
exit 1
