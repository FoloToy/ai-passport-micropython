<div align="center">
  <img src="https://raw.githubusercontent.com/FoloToy/ai-passport/main/assets/images/logo-wordmark-dark.png" alt="FoloToy AI Passport" width="260">
  <h1>FoloToy AI Passport MicroPython</h1>
  <p><strong>Wear it. Flash it. Make it anything.</strong></p>
  <p>Open wearable AI development for everyone.</p>

  <a href="https://github.com/FoloToy/ai-passport-micropython/releases"><img src="https://img.shields.io/github/v/release/FoloToy/ai-passport-micropython?style=flat-square&label=firmware" alt="Firmware releases"></a>
  <a href="https://github.com/FoloToy/ai-passport-micropython/actions"><img src="https://img.shields.io/github/actions/workflow/status/FoloToy/ai-passport-micropython/release-firmware.yml?style=flat-square&label=build" alt="Build status"></a>
  <a href="https://github.com/FoloToy/ai-passport-micropython/blob/main/LICENSE"><img src="https://img.shields.io/github/license/FoloToy/ai-passport-micropython?style=flat-square" alt="License"></a>
</div>

<p align="center">
  <img src="https://raw.githubusercontent.com/FoloToy/ai-passport/main/assets/images/home.jpg" alt="AI Passport hardware" width="760">
</p>

## What this project is

This is the MicroPython development workspace for FoloToy AI Passport. It lets a person with no programming background describe an idea to an AI agent, answer a few simple questions, and turn the idea into a working wearable application.

The project includes:

- A ready-to-use ESP32-C3 firmware target for the AI Passport board.
- Basic MicroPython access to the display, buttons, audio, battery, Wi-Fi, and Bluetooth.
- A simple `main.py` workflow for most applications.
- An advanced source-build workflow for new low-level APIs and drivers.
- English-first documentation with matching Simplified Chinese guides.
- GitHub Actions that build and release a merged firmware image when a `v*` tag is pushed.

## Start with one sentence

Tell the AI what you want in plain language:

> Make a small reminder device: show the time on startup, use the up and down buttons to choose a reminder, press OK to confirm, and play a sound at the reminder time.

The AI should ask one short follow-up question at a time, show a small working screen first, and then add features one by one. You do not need to understand the hardware before starting.

## Choose your development path

| What you want | Recommended path |
| --- | --- |
| A new screen, game, interaction, sound, battery view, Wi-Fi, or Bluetooth feature | **User script** |
| A new C API, I²S MCLK change, LVGL internals, driver, boot flow, memory layout, or partition | **Custom firmware** |

### 1. User script — recommended

Keep the supplied firmware and replace only `main.py`:

```bash
python -m pip install --upgrade mpremote esptool
tools/upload_main.sh ./main.py
```

After reset, `/main.py` runs automatically and takes precedence over the built-in example. To restore the built-in example:

```bash
tools/remove_user_main.sh
```

Create your own UI and flow. The bundled hardware menu is a learning reference, not a product interface to rename or recolour.

### 2. Custom firmware — advanced

Use ESP-IDF 5.5.3 and build the board target:

```bash
tools/build_default_firmware.sh
tools/flash_firmware.sh ports/esp32/build-FOLOTOY_AI_PASSPORT-merged.bin
```

The merged image is written from `0x0`. Windows users should use WSL2 Ubuntu for firmware compilation; native Windows is fully supported for script upload and serial testing.

## Hardware at a glance

| Part | Board capability |
| --- | --- |
| MCU | ESP32-C3, 8 MB flash, no PSRAM |
| Display | 240×320 ST7789, RGB565, 80 MHz SPI |
| Audio | ES8311 codec with I²S MCLK support |
| Input | Three-button ADC ladder |
| Battery | CW2017 voltage and percentage |
| Wireless | 2.4 GHz Wi-Fi and BLE |
| User files | FAT partition with `/main.py` priority |

Pin details and API examples are in [`docs/hardware-and-apis.md`](docs/hardware-and-apis.md).

## Windows and other platforms

- **Windows script development:** install Python and `mpremote`, then use the `COMx` port.
- **Windows firmware development:** use WSL2 Ubuntu with ESP-IDF 5.5.3.
- **macOS/Linux:** use the included shell helpers and the detected USB serial port.
- **USB behaviour:** ESP32-C3 provides USB Serial/JTAG, not USB OTG mass storage. Upload with `mpremote`; it is not a drag-and-drop USB disk.

See [`docs/environment-setup.md`](docs/environment-setup.md) for step-by-step setup.

## Documentation

| Guide | Purpose |
| --- | --- |
| [`AGENTS.md`](AGENTS.md) | Entry point and AI delivery rules |
| [`docs/ai-workflow.md`](docs/ai-workflow.md) | Plain-language AI workflow |
| [`docs/requirements-template.md`](docs/requirements-template.md) | Short questions for clarifying an idea |
| [`docs/quick-start.md`](docs/quick-start.md) | First `main.py` application |
| [`docs/script-development.md`](docs/script-development.md) | Script APIs and application patterns |
| [`docs/device-testing.md`](docs/device-testing.md) | Upload and on-device acceptance |
| [`docs/environment-setup.md`](docs/environment-setup.md) | Windows, WSL2, macOS, Linux, and CI |
| [`docs/firmware-development.md`](docs/firmware-development.md) | Custom firmware build and flash |
| [`docs/troubleshooting.md`](docs/troubleshooting.md) | Common problems and fixes |

Every project guide has an English default file and a matching [`*.zh_CN.md`](docs/README.zh_CN.md) version.

## Firmware releases

Maintainers can create a release by pushing a version tag:

```bash
git tag v0.1.0
git push origin v0.1.0
```

GitHub Actions builds the board, creates a merged image and SHA-256 checksum, and attaches both files to the release. A manual workflow run creates an artifact without publishing a release.

## License

This project follows the upstream MicroPython license. See [`LICENSE`](LICENSE) and [`ACKNOWLEDGEMENTS`](ACKNOWLEDGEMENTS).
