# AI agent workflow (plain-language guide)

This project is for people who may not know programming. The AI should guide the user one small question at a time, using ordinary words. Do not ask the user to fill a long technical form before showing progress.

## 1. Start with one sentence

Ask: “你想让这个小设备做什么？” Then ask only the next missing detail. A useful order is:

1. What should appear when it starts?
2. What should happen when the user presses each button?
3. What should the screen look like (colour, words, pictures)?
4. Does it need sound, recording, Wi-Fi, Bluetooth, battery display, or sleep?
5. How will the user know it works?

Repeat the plan in plain language and let the user correct it. Use [`requirements-template.md`](requirements-template.md) as a checklist, not as a form the user must understand.

## 2. Choose the simple route first

Use the default user-script route unless the request clearly needs a firmware change. The AI writes `main.py`, uploads it over USB, and the user can try it immediately. This is enough for new screens, games, button interactions, audio, battery, Wi-Fi, and Bluetooth features.

Use custom firmware only when the user needs a new low-level API, I²S/MCLK, LVGL internals, a C driver, boot behaviour, memory layout, or partitions. Explain why before choosing this slower route.

The bundled example is only a learning reference. A real product must have its own UI and flow; do not simply rename or recolour the test menu.

## 3. Build in small steps

Show a first working screen, then add one feature at a time. After each complete user-requested change, offer to run it on the board. If no board is detected, tell the user to power it on and connect a data-capable USB cable.

Keep slow work (audio, scanning, networking, and file access) out of button callbacks. Protect LVGL calls with the board's LVGL context rules. A successful build is not proof that the device works; report build, host-test, and device-test results separately.

## 4. Keep the user safe

Never ask for passwords or private keys in source code. Do not commit, push, or open a pull request unless the user asks. Keep the English document as the default and maintain the matching Simplified Chinese document.
