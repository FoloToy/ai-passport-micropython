# 自定义 MicroPython 固件开发

只有默认脚本无法满足需求时才使用本流程。高级开发修改的是 MicroPython 源码和固件，不是简单上传 `main.py`。

## 环境准备

推荐 Ubuntu/Debian。安装 Git、Python 3、CMake、Ninja 和串口工具，初始化子模块，并使用 ESP-IDF 5.5.3：

```bash
git submodule update --init --recursive
source /home/cjiio/.espressif/v5.5.3/esp-idf/export.sh
```

如果 ESP-IDF 不在该路径，设置 `IDF_PATH` 后运行构建脚本。不要混用不同 ESP-IDF 版本。

## 构建默认板卡固件

```bash
tools/build_default_firmware.sh
```

脚本构建 ESP32-C3、8 MB Flash、LVGL 和 AI Passport 板卡支持，并生成启动器、分区表、应用镜像和合并镜像。分区表当前为 3 MiB 应用区和 5 MiB 用户 FAT 区；如果应用继续增大，必须重新评估分区。

## 修改和验证

修改前执行 `git status --short --branch`，保留用户已有修改。先编译，再检查分区表和镜像大小；成功编译不等于实机验证。

## 串口烧录

```bash
tools/flash_firmware.sh ports/esp32/build-FOLOTOY_AI_PASSPORT-merged.bin
tools/device_info.sh
```

设备使用 ESP32-C3 USB Serial/JTAG。烧录固件不要求备份原应用，不代表允许全片擦除。

## 高级需求输入

用户必须说明要改的源文件、运行时行为、兼容旧脚本的要求、内存/Flash 预算、设备验收步骤和是否需要新 API。AI 不应因为“想要更方便的 API”就自动增加高级封装。
