"""One-shot LVGL display smoke test for ``mpremote run``.

The default minimal partition table has no filesystem, so this example is
intentionally self-contained and can be run without copying files:

    mpremote connect /dev/ttyACM0 run lvgl_smoke.py
"""

import micropython
import time
import machine
from machine import Pin, SPI
import lvgl as lv


class Panel:
    def __init__(self):
        self.spi = SPI(1, baudrate=80_000_000, polarity=0, phase=0,
                       sck=Pin(8), mosi=Pin(9), miso=None)
        self.cs = Pin(1, Pin.OUT, value=1)
        self.dc = Pin(20, Pin.OUT, value=1)
        self.bl = Pin(21, Pin.OUT, value=0)
        self.cmd(0x01)
        time.sleep_ms(120)
        self.cmd(0x11)
        time.sleep_ms(120)
        self.cmd(0x3A, b"\x55")
        self.cmd(0x36, b"\x00")
        self.cmd(0x21)
        self.cmd(0x13)
        self.cmd(0x29)
        self.bl.value(1)

    def cmd(self, command, data=b""):
        self.cs.value(0)
        self.dc.value(0)
        self.spi.write(bytes((command,)))
        if data:
            self.dc.value(1)
            self.spi.write(data)
        self.cs.value(1)

    def flush(self, area, pixels):
        x0, y0, x1, y1 = area.x1, area.y1, area.x2, area.y2
        self.cmd(0x2A, bytes((x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF)))
        self.cmd(0x2B, bytes((y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF)))
        self.cs.value(0)
        self.dc.value(0)
        self.spi.write(b"\x2C")
        self.dc.value(1)
        self.spi.write(pixels)
        self.cs.value(1)


panel = Panel()
lv.init()
timer = machine.Timer(0)


def tick(_):
    lv.tick_inc(20)
    try:
        micropython.schedule(handler_ref, 0)
    except RuntimeError:
        pass


def handler(_):
    lv.timer_handler()


handler_ref = handler
draw_buf = bytearray(240 * 40 * 2)
display = lv.display_create(240, 320)
display.set_color_format(lv.COLOR_FORMAT.RGB565)
display.set_buffers(draw_buf, draw_buf, len(draw_buf),
                    lv.DISPLAY_RENDER_MODE.PARTIAL)


def flush_cb(disp, area, color_p):
    width = area.x2 - area.x1 + 1
    height = area.y2 - area.y1 + 1
    pixels = color_p.__dereference__(width * height * 2)
    for index in range(0, len(pixels), 2):
        pixels[index], pixels[index + 1] = pixels[index + 1], pixels[index]
    panel.flush(area, pixels)
    disp.flush_ready()


display.set_flush_cb(flush_cb)
timer.init(mode=Timer.PERIODIC, period=20, callback=tick)
screen = lv.screen_active()
screen.set_style_bg_color(lv.color_hex(0x000000), lv.PART.MAIN)
label = lv.label(screen)
label.set_text("AI PASSPORT\nLVGL READY")
label.align(lv.ALIGN.CENTER, 0, 0)
time.sleep_ms(5000)
print("LVGL_ST7789_SMOKE_PASS")
