# AI Passport MicroPython AI 工作规范

这是 FoloToy AI Passport 的 MicroPython 开发仓库。AI 接收到用户需求后，必须先读取本文件，再读取对应的 `docs/` 文档；不要直接假设用户需要修改 MicroPython C 源码。

## 开发方式选择

默认选择“用户脚本开发”：使用已经编译好的 AI Passport 固件，只在设备文件系统中上传 `main.py`。只有用户明确需要新增底层能力、修改解释器、修改 I²S/LVGL/蓝牙行为或改变固件配置时，才选择“自定义 MicroPython 固件开发”。

AI 必须先确认：用户可见功能和页面流程、使用的外设、脚本还是固件、设备串口和验收步骤。需求不清楚时先使用 `docs/requirements-template.md`。

## 默认脚本路径

1. 从 `ports/esp32/boards/FOLOTOY_AI_PASSPORT/examples/main.py` 开始。
2. 二次开发必须重新设计自己的 UI，不得把硬件测试菜单作为产品 UI。
3. 使用标准 `machine` 接口和板级基础模块；不要创建未经需求授权的高级封装层。
4. 用 `tools/upload_main.sh` 上传并重启。
5. 通过串口日志、屏幕和实际按键完成验收。

## 高级固件路径

1. 按 `docs/firmware-development.md` 准备 ESP-IDF 5.5.3、编译器和子模块。
2. 修改前检查 `git status --short --branch`，保留用户已有修改。
3. 板级逻辑放在 `ports/esp32/boards/FOLOTOY_AI_PASSPORT` 或端口代码；应用示例放在 `examples/`。
4. 使用 `tools/build_default_firmware.sh` 构建，使用 `tools/flash_firmware.sh` 通过串口烧录。
5. 不要把构建目录、临时日志、设备私有数据或凭据提交到仓库。

## 硬件事实

- 芯片：ESP32-C3，8 MB Flash，无 PSRAM。
- 显示：240×320 ST7789，SPI(1)，SCLK GPIO8，MOSI GPIO9，CS GPIO1，DC GPIO20，背光 GPIO21。
- 音频：ES8311，I²C `0x18`；I²S MCLK GPIO6、BCLK GPIO5、WS GPIO3、DOUT GPIO2、DIN GPIO4。
- 电池：CW2017，I²C `0x63`；共享 I²C SCL GPIO7、SDA GPIO10。
- 按键：GPIO0 ADC 电阻分压。
- USB：ESP32-C3 USB Serial/JTAG，不是 USB OTG MSC，不能承诺 U 盘拖拽。

## 交付前检查

```text
Build: PASS / FAIL / NOT RUN
Host tests: PASS / FAIL / NOT RUN
Device tests: PASS / FAIL / NOT RUN
Unverified: 仍需用户或实机确认的内容
```

用户明确要求后才提交或推送。完成固件功能后主动询问是否需要刷写；已有明确授权时可按授权执行。
