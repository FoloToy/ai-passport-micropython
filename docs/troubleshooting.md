# Troubleshooting

## The board is not found

Power it on and use a data-capable USB cable. Run `tools/find_port.sh`. Close other serial tools and check Linux permissions. The ESP32-C3 USB interface is serial, not a USB disk.

## `main.py` did not change

Reset after upload and check the file:

```bash
python -m mpremote connect /dev/ttyACM0 fs ls
python -m mpremote connect /dev/ttyACM0 exec "print(open('/main.py').read()[:80])"
```

Remove the user file with `tools/remove_user_main.sh` to restore the frozen example.

## Chinese text is blank or shown as boxes

The default font may not contain Chinese glyphs. Use a font with the required characters, select it for the exact widget, save the source as UTF-8, and verify the result on the board. A successful build alone does not prove glyph coverage.

## Audio or scanning freezes the UI

Move the operation to a worker/state machine, add a timeout, and let the UI show `starting`, `ready`, `failed`, or `timeout`. Never perform long I²S, Wi-Fi, BLE, or file operations inside a button callback.

## Custom firmware will not build

Check ESP-IDF 5.5.3 is activated, submodules are present, and the board name is exactly `FOLOTOY_AI_PASSPORT`. Run the build script again and keep the first error, not only the final summary.
