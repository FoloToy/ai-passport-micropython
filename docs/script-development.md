# User-script development: AI implementation guide

This document is primarily for the AI agent. The user should only need to describe the desired behaviour in ordinary language. The agent turns that description into a small script, uploads it, and explains the observed result.

## Agent procedure

1. Read `AGENTS.md`, `docs/ai-workflow.md`, and this guide.
2. Ask one short question for each missing user-visible detail; do not send the user a hardware questionnaire.
3. Decide whether `main.py` is enough. Choose custom firmware only for a missing low-level capability.
4. Pick the nearest example, copy only useful hardware setup, and redesign the UI and flow.
5. Implement one visible milestone first, then add peripherals one at a time.
6. Run syntax checks, upload with `tools/upload_main.sh`, reset, and observe the serial log and screen.
7. Report what was verified, what was not, and the next small test. Do not claim a build is a hardware test.

When the user says “make an app” without details, ask: “开机先显示什么？” Do not copy the hardware-test menu as the product UI.

This is the normal route. Keep the supplied firmware and replace only the user's `main.py`.

## Start from a small app

Copy `ports/esp32/boards/FOLOTOY_AI_PASSPORT/examples/main.py`, remove the demo UI, and design your own screen and flow. The board provides the basic MicroPython modules needed by the examples:

- `machine.Pin`, `machine.PWM`, `machine.ADC`, and `machine.I2S` for pins, backlight, buttons, and audio.
- `st7789` for the 240×320 display.
- `es8311` for codec setup and power control.
- `cw2017` for battery readings.
- `bluetooth` and `network` for BLE and Wi-Fi.

Keep callbacks short. Start a worker or state machine for recording, playback, scans, and network requests. Do not update LVGL objects from an unrelated thread.

## Upload and run

```bash
tools/upload_main.sh ./main.py
python -m mpremote connect /dev/ttyACM0 reset
```

The uploaded file is saved as `/main.py` in the user filesystem and runs after reset. To return to the frozen example:

```bash
tools/remove_user_main.sh
```

## Suggested order

1. Draw one page.
2. Add button state and navigation.
3. Add one peripheral and show its result on screen.
4. Add error and timeout states.
5. Test reset, repeated use, and low-battery behaviour.

For Chinese text, verify that the selected font contains every glyph; the default ASCII font cannot display Chinese characters.
