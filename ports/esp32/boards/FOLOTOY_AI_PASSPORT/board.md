# FoloToy AI Passport

This board definition targets the FoloToy AI Passport: an ESP32-C3 with 8 MB
flash, native USB Serial/JTAG, a 240 × 320 ST7789P3 display, an ES8311 audio
codec, and a CW2017 fuel gauge.

The board exposes the native MicroPython ESP32-C3 port and includes small
`st7789` and `es8311` helper modules under `modules/`.  They are intentionally
thin examples rather than a framework: applications can use the standard `machine.Pin`,
`machine.SPI`, `machine.I2C`, and `machine.I2S` APIs directly, or start from
the helpers and replace the UI/audio policy with their own implementation.

## Pin map

| Alias | GPIO | Function |
| --- | ---: | --- |
| `LCD_SCLK` | 8 | ST7789P3 SPI clock |
| `LCD_MOSI` | 9 | ST7789P3 SPI data |
| `LCD_CS` | 1 | Display chip select |
| `LCD_DC` | 20 | Display data/command |
| `LCD_BL` | 21 | Display backlight |
| `BUTTON_ADC` | 0 | Three-button resistor ladder ADC |
| `I2C_SCL` | 7 | Shared ES8311/CW2017 I²C clock |
| `I2C_SDA` | 10 | Shared ES8311/CW2017 I²C data |
| `ES8311_MCLK` | 6 | Codec master clock |
| `ES8311_BCLK` | 5 | Codec bit clock |
| `ES8311_WS` | 3 | Codec word select |
| `ES8311_DOUT` | 2 | MCU to codec audio data |
| `ES8311_DIN` | 4 | Codec to MCU audio data |

The ES8311 uses 7-bit I²C address `0x18`; the CW2017 uses `0x63`.  The LCD is
on `SPI(1)`, which maps to ESP-IDF SPI2 on ESP32-C3.  USB Serial/JTAG remains
on GPIO18/19 and is the default REPL transport.

## REPL examples

After connecting to the USB Serial/JTAG REPL, run the examples from this
directory (or copy them to the device with `mpremote`):

```python
import display_demo
```

The display helper uses RGB565 and initializes the 240 × 320 panel at 80 MHz.
For audio, the codec must receive MCLK on GPIO6.  The ESP32 port extends the
standard I²S constructor with the optional `mck` keyword:

```python
from machine import I2S, Pin
i2s = I2S(0, sck=Pin(5), ws=Pin(3), sd=Pin(2), mck=Pin(6),
          mode=I2S.TX, bits=16, format=I2S.MONO,
          rate=16000, ibuf=4096)
```

Run `audio_playback.py` for a silent DAC-path check or `audio_record.py` for
one capture buffer.  These examples configure the common 4.096 MHz MCLK
(256 × 16 kHz) / 16 kHz / 16-bit ES8311 mode.  Other sample rates require matching ES8311
clock-divider values; do not change the I²S rate alone.

For a microphone-to-speaker loopback, copy `audio_loopback.py` and run it
after copying `modules/es8311.py`.  It records five seconds to
`loopback.pcm`, switches the I²S channel from RX to TX, plays the recording,
and repeats.  The file is used intentionally so the 160 KiB recording does
not consume the ESP32-C3 heap.  This is sequential RX then TX; it is not
full-duplex monitoring.

## Complete hardware checkout

`examples/hardware_test.py` is a serial-first acceptance example for a bare
AI Passport board. Copy `modules/es8311.py`, `modules/st7789.py`, and the
example to the device, then run:

```python
import hardware_test
```

It checks the shared I²C bus and both device addresses, reads CW2017 voltage,
state-of-charge and configuration, samples the GPIO0 three-button ADC,
initializes ST7789 and shows RGB565 color patterns, verifies the ES8311 active
register state, captures and plays a short I²S buffer, and scans nearby
2.4-GHz Wi-Fi networks. Each step prints a `PASS` or `FAIL` line. The script
does not rewrite the battery profile and does not enter deep sleep; run the
normal low-power example separately after the basic hardware checkout.

For a continuously running on-device menu, copy the same modules plus
`examples/hardware_menu.py`, then run:

```python
import hardware_menu
```

The display shows the selected test. GPIO0 buttons navigate up/down and start
the selected item. Each item opens a dedicated result screen; after the test
finishes, hold button 3 (OK) for about one second to return to the menu.
`RUN ALL` executes every peripheral check and then shows its aggregate result.
The result screen lists each check point separately; if the list is longer than
the display, the remaining details stay available in the USB serial log.
The Wi-Fi result page additionally lists discovered SSIDs, RSSI and channel;
the button page lists the idle reading and each button's PASS/FAIL state.
Press Ctrl-C in the USB REPL to stop it. The menu uses a small
ASCII pixel font so it does not depend on a particular LVGL or Chinese font.

The ES8311 and CW2017 share I²C.  Stop I²S before calling `ES8311.sleep()` and
do not use the shared bus while the codec is being put into sleep.

## LVGL display example

This board variant builds the official LVGL v9 MicroPython binding.  The
binding is not enabled by the stock ESP32 boards; select
`FOLOTOY_AI_PASSPORT` when building to include the `lvgl` module.  The
ST7789 adapter uses SPI(1) at 80 MHz, RGB565, and a partial draw buffer so the
ESP32-C3 does not need a full-screen framebuffer.

Copy `modules/st7789.py`, `modules/lv_utils.py`,
`modules/lvgl_st7789.py`, and `examples/lvgl_demo.py` to the device, then run:

```python
import lvgl_demo
```

## Replacing `main.py`

ESP32-C3 exposes USB Serial/JTAG rather than a USB OTG mass-storage
controller, so this board cannot appear as a standard drag-and-drop USB flash
drive. The firmware provides a small FAT filesystem and keeps the USB serial
REPL available for file transfer instead:

```bash
mpremote connect /dev/ttyACM0 cp main.py :main.py
```

After reset, `/main.py` on the filesystem takes precedence over the frozen
example. Remove the user file to restore the bundled application:

```bash
mpremote connect /dev/ttyACM0 rm :main.py
```

This replaces only the user script and does not require reading back or
backing up the application image. The application and filesystem sizes are
defined in `partitions-8MiB-ai-passport.csv` and may be adjusted for a larger
user application.

The display page adjusts the backlight with five PWM levels (20%, 40%, 60%,
80%, and 100%). The display test never jumps directly to 0%; complete
backlight shutdown is reserved for the low-power sequence.

## AI Passport application shell

`examples/ai_passport_app.py` is the board's MicroPython application shell. It
uses a product-oriented launcher rather than the hardware checkout menu and
provides four dedicated pages:

- **Music** — checks the ES8311 presence and shows the I²S/MCLK contract.
- **Wi-Fi** — scans nearby 2.4 GHz access points and lists the first results.
- **Device** — displays CW2017 battery/voltage data and the board buses.
- **Sleep** — documents the low-power entry point for an application to wire
  to its own policy.

The three buttons on GPIO0 navigate up/down and open a page; hold OK for about
800 ms to return to the launcher. The app is frozen into the firmware as a
fallback when no user `main.py` exists. Build this board variant,
flash the merged image at `0x0`, and the application starts automatically
after reset. A manual import is only needed when restarting it from the REPL:

```python
import ai_passport_app
```

The frozen `main.py` starts this application automatically after reset when no
user file is present; a user file takes precedence. The shell is
intentionally an application starting point: replace its pages with your own
UI while keeping the reusable `ST7789LVGL`, `st7789`, `es8311`, and standard
`machine` APIs.

The launcher follows the reference AI Passport layout: blue sky background,
cloud and grass footer, offset cream pixel cards in a two-column grid, and the
small mascot at the bottom. The LVGL loop targets 50 Hz and uses
`RGB565_SWAPPED`, allowing the ST7789 flush callback to send the partial buffer
without a per-pixel Python byte-swap loop. This keeps animation and navigation
responsive on the ESP32-C3 while retaining the 80 MHz SPI setting.

The detail pages also follow the reference demos: the display color swatch,
button ADC readout with live UP/DOWN/OK and PRESS/RELEASE/LONG event status,
audio record/tone card, battery percentage and CW2017 voltage panel, Wi-Fi result panel,
Bluetooth advertising panel, and the two low-power mode cards keep the same
geometry, titles, colors, and action hints.

The page actions are wired as well: DISPLAY cycles colors and toggles the
backlight, BUTTON refreshes the ADC value, AUDIO plays a 1 kHz ES8311 tone on
OK, BUTTON shows the current ADC voltage and event log, BATTERY refreshes the
CW2017 reading, WI-FI performs a 2.4 GHz scan and
lists results, BLE starts a three-second GAP scan and displays each device's
advertised name, complete MAC address, and RSSI (long rows scroll), and LOW POWER runs a timed
light-sleep test. Hold OK on any page to return to the launcher.

`lv_utils.event_loop` advances the LVGL tick and schedules `lv.timer_handler`
from a periodic hardware timer.  Application code must keep LVGL calls in the
same execution context as the event loop; do not update widgets from an
interrupt callback.  The example intentionally uses English text so it does
not imply that the default LVGL fonts contain Chinese glyphs.  For Chinese UI,
bundle a font with the required glyph ranges and assign it explicitly to each
widget style.

## Build

From the MicroPython repository root:

```bash
make -C ports/esp32 BOARD=FOLOTOY_AI_PASSPORT
```

The generated firmware can be written with the native USB Serial/JTAG port.  A
full-chip erase is not required for ordinary MicroPython installation; follow
the standard ESP32 deployment instructions when replacing an existing image.

The board definition is validated with the ESP32 port build.  A successful
build verifies the image and API compilation only; verify panel rendering and
audio capture/playback on real hardware.
