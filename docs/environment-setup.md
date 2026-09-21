# Environment setup

The default user-script workflow works on Windows, macOS, and Linux. Only custom firmware compilation needs the full ESP32 toolchain.

## Default workflow (all systems)

Install Python 3.10 or newer, then run:

```text
python -m pip install --upgrade mpremote esptool
```

On Windows, use `py -m pip` if `python` is not recognised. Connect the powered-on board with a data-capable USB cable. Windows normally shows `COM3` or another `COMx`; Linux normally shows `/dev/ttyACM0`; macOS normally shows `/dev/cu.usbmodem*`.

Set the port when needed:

```powershell
$env:AI_PASSPORT_PORT = "COM3"
python -m mpremote connect COM3 exec "print('MicroPython ready')"
```

Then upload with `python -m mpremote connect COM3 resume fs cp .\main.py :main.py`. The Unix helper scripts in `tools/` are convenient on Linux/macOS and WSL; on native Windows use the equivalent `mpremote` command.

## Custom firmware on Windows

The supported Windows route is WSL2 with Ubuntu. Install WSL2 from an Administrator PowerShell:

```powershell
wsl --install -d Ubuntu
```

Inside Ubuntu, install the build tools and clone this repository with its submodules:

```bash
sudo apt update
sudo apt install -y build-essential git cmake ninja-build python3 python3-venv \
    libffi-dev libssl-dev dfu-util libusb-1.0-0
git clone --recursive https://github.com/FoloToy/ai-passport-micropython.git
cd ai-passport-micropython
```

Install or activate ESP-IDF 5.5.3, then run `tools/build_default_firmware.sh`. Flashing can be done from WSL with the USB device passed through, or from Windows PowerShell with `python -m esptool --chip esp32c3 --port COM3 write-flash 0x0 <merged-image>`.

Do not build the full ESP-IDF firmware in native PowerShell unless you already maintain the required compiler and ESP-IDF environment. WSL2 keeps the documented Linux build path consistent with GitHub Actions.

## GitHub Actions release

Pushing a tag such as `v0.1.0` starts `.github/workflows/release-firmware.yml`. It checks out submodules, installs ESP-IDF 5.5.3, builds the `FOLOTOY_AI_PASSPORT` board, creates a merged image from address `0x0`, writes a SHA-256 file, and attaches both files to a GitHub Release. The workflow can also be started manually; a manual run uploads an artifact but does not create a release.
