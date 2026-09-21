"""Minimal LVGL v9 demo for the AI Passport display.

Copy modules/lvgl_st7789.py, modules/lv_utils.py and modules/st7789.py to the
device first, then run ``import lvgl_demo`` from the REPL.
"""

import lvgl as lv
from lvgl_st7789 import ST7789LVGL

display = ST7789LVGL()
screen = lv.screen_active()
screen.set_style_bg_color(lv.color_hex(0x000000), lv.PART.MAIN)

title = lv.label(screen)
title.set_text("AI PASSPORT")
title.align(lv.ALIGN.TOP_MID, 0, 28)

subtitle = lv.label(screen)
subtitle.set_text("Wear it. Flash it. Make it anything.")
subtitle.align(lv.ALIGN.CENTER, 0, 0)

hint = lv.label(screen)
hint.set_text("LVGL + ST7789")
hint.align(lv.ALIGN.BOTTOM_MID, 0, -24)
