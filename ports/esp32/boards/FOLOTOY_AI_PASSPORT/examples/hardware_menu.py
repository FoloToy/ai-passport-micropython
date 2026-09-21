"""Persistent on-device hardware test menu.

Buttons on GPIO0: button 1 = up, button 2 = down, button 3 = select.
Ctrl-C on the USB REPL exits the menu.  Each test returns here when finished.
"""

from machine import ADC, Pin
import time

from st7789 import ST7789
from hardware_test import RESULTS, WIFI_NETWORKS, test_i2c, test_battery, test_buttons
from hardware_test import test_display, test_codec_and_audio, test_wifi


ITEMS = ("RUN ALL", "I2C", "BUTTONS", "DISPLAY", "AUDIO", "WI-FI")
WHITE, BLACK, GREEN, YELLOW, BLUE = 0xFFFF, 0x0000, 0x07E0, 0xFFE0, 0x001F


def button(adc):
    value = adc.read_uv() // 1000 if hasattr(adc, "read_uv") else adc.read()
    if value < 150:
        return 1
    if value < 447:
        return 2
    if value < 1900:
        return 3
    return 0


def draw_menu(lcd, selected, message="SELECT TEST"):
    lcd.fill(BLACK)
    lcd.fill_rect(0, 0, 240, 54, 0x18E3)
    lcd.text("HARDWARE TEST", 16, 10, WHITE, 2, background=0x18E3)
    lcd.text(message[:15], 16, 36, YELLOW, 1, background=0x18E3)
    for index, item in enumerate(ITEMS):
        y = 66 + index * 36
        lcd.fill_rect(12, y, 216, 29, BLUE if index == selected else 0x2104)
        row_color = BLUE if index == selected else 0x2104
        lcd.text((">" if index == selected else " ") + item, 20, y + 7,
                  WHITE, 2, background=row_color)
    lcd.fill_rect(0, 290, 240, 30, 0x18E3)
    lcd.text("1 UP  2 DOWN  3 OK", 12, 300, WHITE, 1, background=0x18E3)


def draw_test_screen(lcd, name, status, color=WHITE):
    lcd.fill(BLACK)
    lcd.fill_rect(0, 0, 240, 54, 0x18E3)
    lcd.text("HARDWARE TEST", 16, 10, WHITE, 2, background=0x18E3)
    lcd.text(name[:15], 16, 36, YELLOW, 1, background=0x18E3)
    lcd.fill_rect(12, 78, 216, 84, 0x2104)
    lcd.text(status[:17], 22, 105, color, 2, background=0x2104)
    lcd.fill_rect(0, 290, 240, 30, 0x18E3)
    lcd.text("HOLD OK TO RETURN", 22, 300, WHITE, 1, background=0x18E3)


def wait_return(adc):
    # Do not treat the menu's select click as the return gesture.
    while button(adc):
        time.sleep_ms(40)
    started = None
    while True:
        key = button(adc)
        now = time.ticks_ms()
        if key == 3:
            if started is None:
                started = now
            elif time.ticks_diff(now, started) >= 1000:
                while button(adc):
                    time.sleep_ms(40)
                return
        else:
            started = None
        time.sleep_ms(40)


def draw_result_screen(lcd, name):
    lcd.fill(BLACK)
    lcd.fill_rect(0, 0, 240, 54, 0x18E3)
    lcd.text("TEST RESULT", 16, 10, WHITE, 2, background=0x18E3)
    lcd.text(name[:15], 16, 36, YELLOW, 1, background=0x18E3)
    rows = RESULTS[:8]
    if name == "WI-FI" and WIFI_NETWORKS:
        lcd.text("SSID        RSSI CH", 12, 62, YELLOW, 1, background=BLACK)
        for index, (ssid, rssi, channel) in enumerate(WIFI_NETWORKS[:8]):
            y = 80 + index * 24
            lcd.text("%-12s %4d %2d" % (ssid, rssi, channel), 12, y,
                     WHITE, 1, background=BLACK)
        if len(WIFI_NETWORKS) > 8:
            lcd.text("+%d MORE IN USB LOG" % (len(WIFI_NETWORKS) - 8),
                     12, 274, YELLOW, 1, background=BLACK)
        rows = []
    for index, (check, ok) in enumerate(rows):
        y = 62 + index * 25
        bg = 0x0320 if ok else 0xC000
        label = ("PASS " if ok else "FAIL ") + check[:13]
        lcd.fill_rect(10, y, 220, 21, bg)
        lcd.text(label, 16, y + 6, WHITE, 1, background=bg)
    if len(RESULTS) > len(rows):
        lcd.text("+%d MORE IN USB LOG" % (len(RESULTS) - len(rows)),
                 16, 270, YELLOW, 1, background=BLACK)
    lcd.fill_rect(0, 290, 240, 30, 0x18E3)
    lcd.text("HOLD OK TO RETURN", 22, 300, WHITE, 1, background=0x18E3)


def run_one(index, lcd, adc):
    name = ITEMS[index]
    draw_test_screen(lcd, name, "RUNNING")
    print("\n=== %s ===" % name)
    RESULTS.clear()
    try:
        if index == 0:
            bus = test_i2c()
            test_battery(bus)
            test_buttons()
            test_display()
            test_codec_and_audio()
            test_wifi()
        elif index == 1:
            test_battery(test_i2c())
        elif index == 2:
            test_buttons()
        elif index == 3:
            test_display()
        elif index == 4:
            test_codec_and_audio()
        elif index == 5:
            test_wifi()
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        print("[FAIL] %s: %r" % (name, exc))
    failed = sum(1 for _, ok in RESULTS if not ok)
    draw_result_screen(lcd, name)
    wait_return(adc)


def run():
    print("FoloToy AI Passport persistent hardware menu")
    print("Button 1=UP, Button 2=DOWN, Button 3=SELECT; Ctrl-C exits")
    adc = ADC(Pin(0))
    adc.atten(ADC.ATTN_11DB)
    lcd = ST7789()
    selected = 0
    draw_menu(lcd, selected)
    last = 0
    while True:
        key = button(adc)
        now = time.ticks_ms()
        if key and key != last:
            if key == 1:
                selected = (selected - 1) % len(ITEMS)
            elif key == 2:
                selected = (selected + 1) % len(ITEMS)
            else:
                run_one(selected, lcd, adc)
            draw_menu(lcd, selected)
        last = key
        time.sleep_ms(50)


run()
