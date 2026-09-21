# Simple requirement conversation

Do not make a non-technical user fill every line. Ask these questions one by one and write down the answers:

1. **Goal:** “你希望它帮你做什么？”
2. **Start:** “开机后先看到什么？”
3. **Buttons:** “上下和确认键分别做什么？短按和长按要区分吗？”
4. **Screen:** “想显示哪些字、图片或颜色？需要中文吗？”
5. **Sound:** “需要播放、录音，还是两者都要？什么时候可以打断？”
6. **Connections:** “需要 Wi-Fi 或蓝牙做什么？”
7. **Battery:** “要显示电量吗？多久不用后休眠？”
8. **Finish line:** “做到什么现象，就算完成？”

If the user does not know an answer, propose a sensible default and ask for confirmation. Keep a short summary such as:

```text
我要做一个“桌面提醒器”。开机显示时间；上下键切换提醒，确认键查看详情；需要中文和提示音；暂时不用 Wi-Fi；5 分钟无操作后休眠。完成标准：能显示、能切换、能响铃、能唤醒。
```

Only ask technical details when they affect the result (for example, a serial port or a custom firmware change). If the user only says “make an app”, do not copy the test menu—continue this conversation until the app's pages and actions are clear.
