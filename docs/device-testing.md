# Uploading and testing on the board

## Before connecting

Power on the AI Passport and connect it with a data-capable USB cable. USB Serial/JTAG appears as `/dev/ttyACM0` on Linux in most setups or as `COMx` on Windows. Find it with:

```bash
tools/find_port.sh
```

If no port is found, keep the board powered on, reconnect the cable, and check permissions or another USB port. The C3 does not provide USB mass-storage drag-and-drop.

## Script test

```bash
tools/upload_main.sh ./main.py
python -m mpremote connect /dev/ttyACM0 reset
python -m mpremote connect /dev/ttyACM0 repl
```

Check the boot screen, every button action, audio start/stop, scan timeout, and recovery after reset. A test is not complete until the user-visible acceptance steps work on the board.

## Firmware test

Use [`firmware-development.md`](firmware-development.md) to build and flash a merged image. Record the exact board, image, serial port, and observed result. Do not treat a successful compile as device validation.

## Report format

```text
Build: PASS / FAIL / NOT RUN
Host tests: PASS / FAIL / NOT RUN
Device tests: PASS / FAIL / NOT RUN
Unverified: remaining board, instrument, or user checks
```
