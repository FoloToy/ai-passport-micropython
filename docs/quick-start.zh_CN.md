# 默认脚本开发快速开始（AI 指南）

本页是给 AI 智能体执行的清单，不是要求用户自己学习的技术教程。

默认脚本开发不修改 MicroPython 源码，适合新页面、游戏、交互、音频和网络应用。普通用户只要用白话告诉 AI 想做什么，AI 会一次问一个补充问题。

每次接到需求后，AI 应该：

1. 用白话复述用户想要的体验。
2. 只追问下一个缺少的信息。
3. 先生成一个重新设计 UI 的最小 `main.py`。
4. 上传运行后，再加入下一个功能。
5. 把代码检查结果和实机现象分开说明。

可以这样开始：

```text
做一个桌面提醒器：开机显示时间，上下键选择提醒，按确认键确定，到时间播放提示音。
```

## 环境

```bash
python -m pip install mpremote
python -m mpremote connect /dev/ttyACM0 exec "print('MicroPython ready')"
```

Windows 将 `/dev/ttyACM0` 替换为 `COMx`。串口可用 `tools/find_port.sh` 查询。没有设备时，提示用户打开设备并使用数据线连接电脑 USB 口。

## 创建和上传

从 `ports/esp32/boards/FOLOTOY_AI_PASSPORT/examples/main.py` 开始，重新设计自己的页面，不要直接复用测试菜单。上传：

```bash
tools/upload_main.sh ./main.py
```

`main.py` 会在设备启动时自动运行；用户文件优先于固件内置示例。删除用户文件可恢复内置示例：

```bash
tools/remove_user_main.sh
```

## 推荐迭代顺序

1. 先只显示一个页面。
2. 加入按键状态和页面切换。
3. 单独加入屏幕绘制。
4. 再加入音频、网络、电池和低功耗。
5. 每次只增加一个外设，上传并验证。
