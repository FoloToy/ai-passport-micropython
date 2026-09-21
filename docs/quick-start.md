# Default user-script quick start (AI guide)

This page is an execution checklist for the AI agent, not a form that the user must study.

The default path does not modify MicroPython source. It is suitable for new pages, games, interactions, audio, and networking. A non-technical user can simply tell the AI the desired behaviour; the AI should ask one simple follow-up question at a time.

For every request, the AI should:

1. Restate the desired user experience in plain language.
2. Ask only the next missing question.
3. Create a minimal `main.py` with a newly designed UI.
4. Upload and run it before adding the next feature.
5. Report device evidence separately from code checks.

Example first message:

```text
Make a small reminder device: show the time on startup, use UP/DOWN to choose a reminder, press OK to confirm, and play a sound at the reminder time.
```

## Host setup

```bash
python -m pip install mpremote
python -m mpremote connect /dev/ttyACM0 exec "print('MicroPython ready')"
```

Replace `/dev/ttyACM0` with `COMx` on Windows. Use `tools/find_port.sh` to locate a port. If none is found, ask the user to power on the board and connect a data-capable USB cable.

## Create and upload

Start from `ports/esp32/boards/FOLOTOY_AI_PASSPORT/examples/main.py`, redesign the pages, and do not ship the test menu as the product UI:

```bash
tools/upload_main.sh ./main.py
```

The user file runs automatically after reset and takes precedence over the frozen example. Run `tools/remove_user_main.sh` to restore the bundled example.

## Iteration order

Start with one screen, add button state and navigation, then add display rendering, audio, networking, battery, and low power one subsystem at a time.
