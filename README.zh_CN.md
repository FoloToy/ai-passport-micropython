<div align="center">
  <img src="https://raw.githubusercontent.com/FoloToy/ai-passport/main/assets/images/logo-wordmark-dark.png" alt="FoloToy AI Passport" width="260">
  <h1>FoloToy AI Passport MicroPython</h1>
  <p><strong>Wear it. Flash it. Make it anything.</strong></p>
  <p>人人都能使用的开放式可穿戴 AI 开发平台</p>
</div>

<p align="center">
  <img src="https://raw.githubusercontent.com/FoloToy/ai-passport/main/assets/images/home.jpg" alt="AI Passport 硬件" width="760">
</p>

## 这是做什么的

这是 FoloToy AI Passport 的 MicroPython 开发项目。即使用户不会编程，也可以用白话告诉 AI 想做什么，回答几个简单问题，就能把想法变成可运行的可穿戴应用。

项目包含：

- AI Passport ESP32-C3 开箱可用的 MicroPython 固件目标。
- 屏幕、按键、音频、电池、Wi-Fi 和蓝牙的基础 MicroPython 接口。
- 适合大多数应用的 `main.py` 快速开发流程。
- 面向底层 API 和驱动修改的高级源码编译流程。
- 英文默认、中文配套的完整开发文档。
- 推送 `v*` tag 后自动编译并发布合并固件的 GitHub Actions。

## 先用一句话告诉 AI

例如：

> 做一个桌面提醒器：开机显示时间，上下键选择提醒，按确认键确定，到时间播放提示音。

AI 应该一次只问一个简短问题，先做出一个能显示的版本，再逐步加入按键、声音和网络功能。用户不需要先了解硬件。

## 选择开发方式

| 想实现的功能 | 推荐方式 |
| --- | --- |
| 新界面、游戏、交互、声音、电池、Wi-Fi 或蓝牙功能 | **用户脚本** |
| 新增 C API、修改 I²S MCLK、LVGL 内部、驱动、启动流程、内存或分区 | **自定义固件** |

### 1. 用户脚本（推荐）

保留现有固件，只替换 `main.py`：

```bash
python -m pip install --upgrade mpremote esptool
tools/upload_main.sh ./main.py
```

设备重启后会自动运行 `/main.py`，并优先于固件内置示例。恢复内置示例：

```bash
tools/remove_user_main.sh
```

请重新设计自己的产品界面和流程。固件里的硬件测试菜单只是学习参考，不能直接改名或换颜色后作为产品界面。

### 2. 自定义固件（高级）

使用 ESP-IDF 5.5.3 编译板卡目标：

```bash
tools/build_default_firmware.sh
tools/flash_firmware.sh ports/esp32/build-FOLOTOY_AI_PASSPORT-merged.bin
```

合并固件从 `0x0` 开始烧录。Windows 用户建议用 WSL2 Ubuntu 编译固件；脚本上传和串口测试完全支持原生 Windows。

## 硬件概览

| 部件 | 能力 |
| --- | --- |
| 主控 | ESP32-C3，8 MB Flash，无 PSRAM |
| 屏幕 | 240×320 ST7789，RGB565，SPI 80 MHz |
| 音频 | 支持 I²S MCLK 的 ES8311 编解码器 |
| 输入 | 三键 ADC 电阻分压 |
| 电池 | CW2017 电压和电量 |
| 无线 | 2.4 GHz Wi-Fi 和 BLE |
| 用户文件 | FAT 分区，`/main.py` 优先运行 |

硬件引脚和 API 示例见 [`docs/hardware-and-apis.md`](docs/hardware-and-apis.md)。

## Windows 和其他系统

- **Windows 脚本开发：** 安装 Python 和 `mpremote`，使用 `COMx` 串口。
- **Windows 固件开发：** 使用 WSL2 Ubuntu 和 ESP-IDF 5.5.3。
- **macOS/Linux：** 使用仓库内脚本和自动检测到的 USB 串口。
- **USB 说明：** ESP32-C3 是 USB Serial/JTAG，不是 USB OTG 大容量存储设备；使用 `mpremote` 上传，不能像 U 盘一样拖拽文件。

详细步骤见 [`docs/environment-setup.md`](docs/environment-setup.md)。

## 文档

| 文档 | 用途 |
| --- | --- |
| [`AGENTS.md`](AGENTS.md) | AI 入口和交付规则 |
| [`docs/ai-workflow.md`](docs/ai-workflow.md) | 白话 AI 开发流程 |
| [`docs/requirements-template.md`](docs/requirements-template.md) | 逐步澄清需求的问题 |
| [`docs/quick-start.md`](docs/quick-start.md) | 第一个 `main.py` 应用 |
| [`docs/script-development.md`](docs/script-development.md) | 脚本 API 和应用模式 |
| [`docs/device-testing.md`](docs/device-testing.md) | 上传和实机验收 |
| [`docs/environment-setup.md`](docs/environment-setup.md) | Windows、WSL2、macOS、Linux 和 CI |
| [`docs/firmware-development.md`](docs/firmware-development.md) | 自定义固件编译和烧录 |
| [`docs/troubleshooting.md`](docs/troubleshooting.md) | 常见问题排查 |

每份项目文档都有英文默认版本和对应的 [`*.zh_CN.md`](docs/README.zh_CN.md) 中文版本。

## 固件发布

维护者推送版本 tag 即可创建发布：

```bash
git tag v0.1.0
git push origin v0.1.0
```

GitHub Actions 会自动编译板卡、生成合并固件和 SHA-256 校验文件，并附加到 Release。手动运行工作流只生成构建产物，不会发布 Release。

## 许可证

本项目遵循 MicroPython 上游许可证，详见 [`LICENSE`](LICENSE) 和 [`ACKNOWLEDGEMENTS`](ACKNOWLEDGEMENTS)。
