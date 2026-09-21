#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
if [[ -z "${IDF_PATH:-}" ]]; then
    if [[ -f /home/cjiio/.espressif/v5.5.3/esp-idf/export.sh ]]; then
        source /home/cjiio/.espressif/v5.5.3/esp-idf/export.sh
    else
        echo "ESP-IDF 5.5.3 is not activated; set IDF_PATH first." >&2
        exit 1
    fi
fi
export LV_CFLAGS="${LV_CFLAGS:--DLV_COLOR_DEPTH=16}"
make -C "$root/ports/esp32" BOARD=FOLOTOY_AI_PASSPORT -j"${JOBS:-2}"
build="$root/ports/esp32/build-FOLOTOY_AI_PASSPORT"
python -m esptool --chip esp32c3 merge_bin \
    -o "$root/ports/esp32/build-FOLOTOY_AI_PASSPORT-merged.bin" \
    --flash_mode dio --flash_freq 80m --flash_size 8MB \
    0x0 "$build/bootloader/bootloader.bin" \
    0x8000 "$build/partition_table/partition-table.bin" \
    0x10000 "$build/micropython.bin"
