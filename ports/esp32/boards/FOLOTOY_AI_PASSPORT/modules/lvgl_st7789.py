"""LVGL v9 display adapter for the AI Passport ST7789P3 panel."""

import lvgl as lv
import lv_utils
from st7789 import ST7789


class ST7789LVGL:
    def __init__(self, width=240, height=320, buffer_lines=40,
                 spi=None, cs=1, dc=20, bl=21):
        if not lv.is_initialized():
            lv.init()
        self.panel = ST7789(spi=spi, width=width, height=height,
                            cs=cs, dc=dc, bl=bl)

        self.width = width
        self.height = height
        # ST7789 receives 16-bit pixels MSB first.  Let LVGL render in its
        # swapped RGB565 format so the flush path can DMA the buffer directly;
        # byte-swapping each pixel in Python was the main source of low FPS.
        self.color_format = lv.COLOR_FORMAT.RGB565_SWAPPED
        # Keep the draw buffer in a Python bytearray.  This avoids a large
        # allocator call inside LVGL on the no-PSRAM ESP32-C3 and mirrors the
        # binding's portable ``set_buffers`` path.
        self.draw_buf = bytearray(width * buffer_lines * 2)
        self.display = lv.display_create(width, height)
        self.display.set_color_format(self.color_format)
        # Reuse one buffer. A second 19 KiB buffer can trigger collection
        # while LVGL is building its lists on the no-PSRAM target.
        self.display.set_buffers(self.draw_buf, self.draw_buf, len(self.draw_buf),
                                 lv.DISPLAY_RENDER_MODE.PARTIAL)
        self.display.set_flush_cb(self._flush_cb)
        # Start ticking only after LVGL's display and draw buffer are fully
        # initialized; otherwise a timer callback can enter LVGL mid-setup.
        if not lv_utils.event_loop.is_running():
            self.event_loop = lv_utils.event_loop(freq=50)

    def _flush_cb(self, display, area, color_p):
        width = area.x2 - area.x1 + 1
        height = area.y2 - area.y1 + 1
        pixels = color_p.__dereference__(width * height * 2)
        self.panel.blit(pixels, area.x1, area.y1, width, height)
        display.flush_ready()
