# AI Passport hardware and basic APIs

The board target is ESP32-C3 with 8 MB flash, a 240×320 ST7789 display, ES8311 audio codec, CW2017 fuel gauge, three ADC buttons, Wi-Fi, and BLE. Pin assignments are the source in `ports/esp32/boards/FOLOTOY_AI_PASSPORT/mpconfigboard.h` and its board files; do not guess a pin from an internet example.

The examples show the supported starting points:

- Display: initialise ST7789, draw a complete frame, and keep the backlight at a useful PWM level.
- Buttons: sample the ADC and debounce state changes; expose short, long, and released events to the app.
- Audio: initialise ES8311 and I²S, stop a previous stream before starting another, and handle errors without blocking the button callback.
- Battery: read CW2017 voltage and percentage and show an unavailable state when the device does not respond.
- Wi-Fi/BLE: scan only after the user enters the page, use a timeout, and render partial results without overlapping text.

The default app is intentionally small. Higher-level helpers are examples, not a promise that every application should use the demo UI.
