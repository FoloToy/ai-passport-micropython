# AI Passport MicroPython Agent Workflow

This repository is for developing FoloToy AI Passport applications with MicroPython. Read this file first, then read the task-specific English documents under `docs/`. The Chinese pair is available as `*.zh_CN.md`.

## Choose the development path

Use the user-script path by default: keep the prebuilt AI Passport firmware and upload `/main.py`. Choose custom MicroPython firmware only when the request explicitly changes a C API, interpreter behavior, I²S/MCLK, LVGL, BLE, boot flow, memory, or partitions.

Before coding, ask or restate the user-visible behavior, pages, button actions, peripherals, script-versus-firmware choice, serial port, and acceptance criteria. Use `docs/requirements-template.md` when the request is incomplete.

## Default script path

Start from `ports/esp32/boards/FOLOTOY_AI_PASSPORT/examples/main.py`, but redesign the product UI; never ship the hardware-test menu as the application UI. Use standard `machine` APIs and the board modules. Upload with `tools/upload_main.sh` and validate with serial logs, display, buttons, and peripherals.

## Custom firmware path

Read `docs/firmware-development.md`, use ESP-IDF 5.5.3, preserve existing changes after checking `git status --short --branch`, build with `tools/build_default_firmware.sh`, and flash with `tools/flash_firmware.sh`. Do not commit build directories, private logs, credentials, or device data.

## Hardware facts

- ESP32-C3, 8 MB flash, no PSRAM.
- ST7789 240x320: SPI1, SCLK=8, MOSI=9, CS=1, DC=20, backlight=21.
- ES8311 I²C `0x18`: MCLK=6, BCLK=5, WS=3, DOUT=2, DIN=4.
- CW2017 I²C `0x63`; shared SCL=7 and SDA=10.
- Buttons use the GPIO0 ADC ladder.
- USB is ESP32-C3 USB Serial/JTAG, not USB OTG MSC; do not promise drag-and-drop U-disk mode.

## Delivery report

Always report Build, Host tests, Device tests, and Unverified items separately. Do not commit, push, or create a PR unless requested. After a complete firmware change, offer device testing; an existing explicit device-test authorization may be followed.
