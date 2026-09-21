# 上传、运行和实机验收

## 找到串口

```bash
tools/find_port.sh
```

没有设备时，AI 应提示用户打开设备，并使用支持数据传输的 USB 线连接电脑 USB 口。

## 上传脚本

```bash
tools/upload_main.sh path/to/main.py
```

脚本只写入 FAT 用户分区，不要求备份设备原有应用固件，也不会自动执行全片擦除。上传后设备会复位；串口日志用于确认 `main.py` 启动。

## 固件烧录

高级固件使用合并镜像从 `0x0` 烧录：

```bash
tools/flash_firmware.sh ports/esp32/build-FOLOTOY_AI_PASSPORT-merged.bin
```

普通烧录不要求备份原固件；不要把全片擦除作为默认步骤，因为它会删除用户文件系统和配置。

## 验收清单

- 启动日志没有异常重启、栈溢出或 `MemoryError`。
- 屏幕亮起，页面布局没有重叠，中文字体包含所需字形。
- UP、DOWN、OK 短按和长按符合需求。
- 音频播放、录音、停止和异常恢复符合需求。
- Wi-Fi/BLE 扫描不会阻塞页面，结果显示完整。
- 电池电压/电量显示合理。
- 低功耗能进入并按设计唤醒。
- 用户脚本重启后仍然自动运行。
