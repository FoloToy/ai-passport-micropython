# 环境搭建

默认脚本开发支持 Windows、macOS 和 Linux。只有自定义固件编译才需要完整 ESP32 工具链。

## 默认脚本开发（所有系统）

安装 Python 3.10 或更高版本，在 PowerShell、命令提示符或终端执行：

```text
python -m pip install --upgrade mpremote esptool
```

Windows 如果找不到 `python`，使用 `py -m pip`。设备要先开机，并使用支持数据传输的 USB 线连接电脑。Windows 通常显示 `COM3` 一类串口，Linux 通常是 `/dev/ttyACM0`，macOS 通常是 `/dev/cu.usbmodem*`。

Windows 可以这样指定串口并测试：

```powershell
$env:AI_PASSPORT_PORT = "COM3"
python -m mpremote connect COM3 exec "print('MicroPython ready')"
```

上传示例：`python -m mpremote connect COM3 fs cp .\main.py :main.py`。`tools/` 下的 Unix 脚本适合 Linux、macOS 和 WSL，原生 Windows 使用等价的 `mpremote` 命令即可。

## Windows 上开发自定义固件

推荐使用 WSL2 Ubuntu。用管理员 PowerShell 安装：

```powershell
wsl --install -d Ubuntu
```

进入 Ubuntu 后安装工具并递归克隆仓库：

```bash
sudo apt update
sudo apt install -y build-essential git cmake ninja-build python3 python3-venv \
    libffi-dev libssl-dev dfu-util libusb-1.0-0
git clone --recursive https://github.com/FoloToy/ai-passport-micropython.git
cd ai-passport-micropython
```

安装或启用 ESP-IDF 5.5.3 后执行 `tools/build_default_firmware.sh`。烧录可以在 WSL 中配置 USB 透传，也可以回到 Windows PowerShell 执行：`python -m esptool --chip esp32c3 --port COM3 write-flash 0x0 <合并固件>`。

除非已经维护好完整编译器和 ESP-IDF 环境，否则不要直接在原生 PowerShell 中编译完整固件。WSL2 可以保持与 GitHub Actions 一致的 Linux 编译路径。

## GitHub Actions 自动发布

推送类似 `v0.1.0` 的 tag 后，`.github/workflows/release-firmware.yml` 会自动检出子模块、安装 ESP-IDF 5.5.3、编译 `FOLOTOY_AI_PASSPORT`、从 `0x0` 生成合并固件、生成 SHA-256 校验文件，并创建 GitHub Release。也可以手动运行工作流；手动运行只上传构建产物，不创建 Release。
