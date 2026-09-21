# AI Passport 硬件和 API

| 模块 | 硬件 | MicroPython 基础接口 |
| --- | --- | --- |
| 屏幕 | ST7789，240×320，SPI1 | `machine.SPI`、`st7789`、LVGL |
| 背光 | GPIO21 | `machine.PWM`，测试五档亮度 |
| 按键 | GPIO0 ADC 电阻分压 | `machine.ADC` |
| 音频 | ES8311，I²C `0x18` | `machine.I2C`、`machine.I2S` |
| 电池 | CW2017，I²C `0x63` | `machine.I2C` |
| Wi-Fi | ESP32-C3 2.4 GHz | `network.WLAN` |
| BLE | ESP32-C3 NimBLE | `bluetooth.BLE` |
| 用户脚本 | 5 MiB FAT 分区 | `/main.py` |

默认脚本应依赖基础接口，而不是依赖当前演示应用的页面对象。应用 UI、页面状态机和业务逻辑属于用户脚本；芯片和总线初始化才属于板级支持。
