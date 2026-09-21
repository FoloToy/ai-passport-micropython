# Custom MicroPython firmware

Choose this route only when a user-script cannot provide the requested feature. Typical reasons are a new C API, I²S MCLK, a driver change, LVGL internals, boot behaviour, memory limits, or a partition change.

## Prepare the toolchain

Use ESP-IDF 5.5.3 and the normal MicroPython ESP32 prerequisites. From the repository root, activate the ESP-IDF environment, then build the board:

```bash
source /path/to/esp-idf/export.sh
tools/build_default_firmware.sh
```

The build uses `ports/esp32/boards/FOLOTOY_AI_PASSPORT` and produces a merged image at:

```text
ports/esp32/build-FOLOTOY_AI_PASSPORT-merged.bin
```

## Flash and test

```bash
tools/flash_firmware.sh ports/esp32/build-FOLOTOY_AI_PASSPORT-merged.bin
```

The script writes the merged image at address `0x0`. Flashing a new image does not require reading back the old firmware. It may change user files; do not erase the whole chip unless the user explicitly asks.

## Keep changes maintainable

Put reusable board code in the board port or `user_modules`, keep examples small, and document every new API in both English and Simplified Chinese. Add a runnable example and a host-side check where possible. Describe compatibility and user-visible changes before asking for review.
