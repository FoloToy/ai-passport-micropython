"""AI Passport application shell for MicroPython.

This is a small, original UI for the board rather than a copy of the
hardware-test menu.  It keeps the product ideas visible: a glanceable status
bar, a simple launcher, and dedicated pages for the main board capabilities.
The pages intentionally use the public MicroPython peripheral APIs so they can
be replaced by a user's application without changing the display adapter.
"""

import micropython
import time
import _thread
from machine import ADC, I2C, I2S, PWM, Pin, Timer

import lvgl as lv
from lvgl_st7789 import ST7789LVGL


SKY = 0x1689E8
SKY_DARK = 0x0872C9
INK = 0x17202A
PAPER = 0xF4F4EA
GRASS = 0x82BE2D
GRASS_DARK = 0x55951D
YELLOW = 0xFFD928
ORANGE = 0xFFB23E
BLUE = 0x75B9FF
RED = 0xE43B2F


class PassportApp:
    ITEMS = ("Display", "Button", "Audio", "Battery", "Wi-Fi", "BLE", "Low Power")
    DISPLAY_COLORS = (0xFF0000, 0x00FF00, 0x0000FF, 0xFFFFFF, 0x000000)

    def __init__(self):
        self.display = ST7789LVGL(buffer_lines=32)
        self.adc = ADC(Pin(0))
        self.adc.atten(ADC.ATTN_11DB)
        self.i2c = I2C(0, scl=Pin(7), sda=Pin(10), freq=400_000)
        self.screen = None
        self.selected = 0
        self.page = None
        self.down_since = None
        self.last_key = 0
        self.long_sent = False
        self.last_mv = 0
        self.button_log = []
        self.page_status = None
        self.page_results = None
        self.page_rows = []
        self.page_voltage = None
        self.last_battery_ms = 0
        self.display_color = 0
        # Keep the display test usable at every step.  A PWM floor avoids the
        # abrupt all-off transition that made the panel appear dead; level 0
        # is reserved for the actual low-power sequence below.
        self._backlight_duty = (8192, 24576, 40960, 57344, 65535)
        self.backlight_level = 5
        self.backlight = PWM(Pin(21), freq=5000,
                             duty_u16=self._backlight_duty[-1])
        self.ble = None
        self.ble_results = []
        self._ble_records = {}
        self._ble_done_pending = False
        self._ble_result_event = 5
        self._ble_done_event = 6
        self._wifi_busy = False
        self._wifi_pending = False
        self._wifi_rows = []
        self._wifi_error = None
        self._wifi_offset = 0
        self._ble_rows = []
        self._ble_offset = 0
        self._ble_last_render_ms = 0
        self.low_power_mode = 0
        self.audio_busy = False
        self._audio_status_pending = None
        # Poll the resistor-ladder buttons from a hardware timer.  Using an
        # LVGL timer for this made input dependent on the LVGL timer callback
        # bridge and silently dropped presses on some MicroPython builds.
        # The ISR only schedules the Python handler; all ADC/LVGL work stays
        # outside interrupt context.
        self._poll_scheduled = False
        self._button_timer = Timer(1)
        self._button_timer.init(period=70, mode=Timer.PERIODIC,
                                callback=self._button_timer_cb)
        self.show_home()

    def _button_timer_cb(self, _timer):
        if self._poll_scheduled:
            return
        self._poll_scheduled = True
        try:
            micropython.schedule(self._poll_scheduled_handler, 0)
        except RuntimeError:
            self._poll_scheduled = False

    def _poll_scheduled_handler(self, _arg):
        self._poll_scheduled = False
        self._poll(None)

    def _label(self, parent, text, color=INK, size=16):
        obj = lv.label(parent)
        obj.set_text(text)
        obj.set_style_text_color(lv.color_hex(color), 0)
        # The binding's default font is configuration-dependent.  Explicitly
        # selecting the closest bundled font keeps multiline labels from
        # changing their line height and overlapping neighboring widgets.
        font = getattr(lv, "font_montserrat_%d" % size, None)
        if font is None:
            font = getattr(lv, "font_montserrat_16", None)
        if font is not None:
            obj.set_style_text_font(font, 0)
        if hasattr(obj, "set_style_text_line_space"):
            obj.set_style_text_line_space(2, 0)
        return obj

    def _block(self, parent, x, y, width, height, color):
        obj = lv.obj(parent)
        obj.set_pos(x, y)
        obj.set_size(width, height)
        obj.set_style_radius(0, 0)
        obj.set_style_border_width(0, 0)
        obj.set_style_pad_all(0, 0)
        obj.set_style_bg_color(lv.color_hex(color), 0)
        return obj

    def _base(self, title):
        old_screen = self.screen
        self.screen = lv.obj(None)
        self.screen.set_style_bg_color(lv.color_hex(SKY), lv.PART.MAIN)
        self.screen.set_style_pad_all(0, lv.PART.MAIN)
        # Match the reference UI: sky, cloud, grass footer and offset pixel
        # title plate.  These are simple blocks so the style remains fast on
        # the C3 and does not depend on image assets.
        self._block(self.screen, 188, 8, 43, 10, INK)
        self._block(self.screen, 192, 12, 35, 10, PAPER)
        self._block(self.screen, 200, 8, 10, 9, PAPER)
        self._block(self.screen, 215, 9, 9, 8, PAPER)
        self._block(self.screen, 0, 286, 240, 34, GRASS)
        self._block(self.screen, 0, 286, 240, 4, 0xA7D93E)
        for x in range(0, 240, 30):
            self._block(self.screen, x, 312, 18, 8, GRASS_DARK)
            self._block(self.screen, x + 18, 316, 12, 4, 0x75452E)
        self._block(self.screen, 9, 12, 151, 33, INK)
        plate = self._block(self.screen, 5, 8, 151, 33, PAPER)
        plate.set_style_border_color(lv.color_hex(INK), 0)
        plate.set_style_border_width(3, 0)
        heading = self._label(plate, title, INK, 16)
        heading.set_size(140, 24)
        heading.center()
        lv.screen_load(self.screen)
        # Never delete the active LVGL screen. Loading the replacement first
        # also prevents a flush callback from dereferencing a freed tree.
        if old_screen is not None:
            old_screen.delete()
        return self.screen

    def _panel(self, x, y, width, height, color=PAPER, parent=None):
        parent = parent or self.screen
        self._block(parent, x + 5, y + 6, width, height, INK)
        panel = self._block(parent, x, y, width, height, color)
        panel.set_style_border_color(lv.color_hex(INK), 0)
        panel.set_style_border_width(4, 0)
        panel.set_style_pad_all(7, 0)
        return panel

    def _mascot(self, y=242):
        root = self.screen
        self._block(root, 119, y, 3, 6, INK)
        self._block(root, 117, y, 7, 3, ORANGE)
        self._block(root, 104, y + 6, 32, 24, INK)
        self._block(root, 108, y + 10, 24, 16, 0xB9F3FF)
        self._block(root, 112, y + 14, 4, 6, 0x294B7A)
        self._block(root, 124, y + 14, 4, 6, 0x294B7A)
        self._block(root, 113, y + 26, 18, 4, ORANGE)
        self._block(root, 109, y + 30, 22, 11, 0x7557D9)
        self._block(root, 104, y + 32, 5, 7, 0xB9F3FF)
        self._block(root, 131, y + 32, 5, 7, 0xB9F3FF)
        self._block(root, 109, y + 42, 9, 4, INK)
        self._block(root, 122, y + 42, 9, 4, INK)

    def _build_scan_page(self, index):
        """Build an isolated, fixed-row scanner page for Wi-Fi or BLE."""
        title = "WI-FI SCAN" if index == 4 else "BLUETOOTH LE"
        self.page = title
        self.page_status = None
        self.page_results = None
        self.page_rows = []
        root = self._base(title)

        panel = self._panel(8, 50, 224, 226, PAPER)
        status = self._label(panel, "PREPARING...", SKY_DARK, 14)
        status.set_size(208, 22)
        status.set_pos(8, 8)
        self.page_status = status

        # A separate result surface clips every row to the scanner area.
        result_surface = self._block(panel, 8, 38, 208, 166, 0xE7E7D9)
        result_surface.set_style_pad_all(0, 0)
        row_count = 8 if index == 4 else 7
        for row in range(row_count):
            label = self._label(result_surface, "", INK, 14)
            label.set_size(204, 20)
            label.set_pos(2, row * 20)
            if index == 5:
                try:
                    label.set_long_mode(lv.LABEL_LONG.SCROLL_CIRCULAR)
                except Exception:
                    pass
            self.page_rows.append(label)
        self.page_rows[0].set_text("RSSI  SSID  CHANNEL" if index == 4 else "NAME | MAC ADDRESS | RSSI")

        footer = self._label(panel, "UP/DN PAGE   OK RESCAN   HOLD OK BACK", INK, 12)
        footer.set_size(208, 20)
        footer.set_pos(8, 208)
        self._scan_kind = index
        lv.screen_load(root)
        # Scan as soon as the page is visible so the result rows fill in
        # without an extra OK press.  The scan blocks for a couple of seconds,
        # so it must run from a scheduled callback after LVGL has presented
        # the page, not while the screen tree is being built.
        try:
            micropython.schedule(self._start_page_scan, index)
        except RuntimeError:
            pass

    def _discard_press(self):
        """Forget the in-flight OK press after a blocking scan.

        WLAN.scan() and BLE scanning stall _poll() for a couple of seconds.
        The release is detected only after the scan returns, so the measured
        hold time would include the scan and a normal tap would look like a
        long press, sending the user straight back to the launcher.
        """
        self.down_since = None
        self.long_sent = False
        self.last_key = 0

    def _reference_page(self, index):
        names = ("DISPLAY", "BUTTON / ADC", "AUDIO", "BATTERY",
                 "WI-FI SCAN", "BLUETOOTH LE", "LOW POWER")
        self.page = names[index]
        self.page_status = None
        self.page_results = None
        self.page_rows = []
        self.page_voltage = None
        if index in (4, 5):
            self._build_scan_page(index)
            return
        root = self._base(names[index])
        if index == 0:
            panel = self._panel(18, 58, 204, 188,
                                self.DISPLAY_COLORS[self.display_color])
            text = self._label(panel, "%s\n\nBACKLIGHT %d%%\n\nOK: NEXT COLOR\nUP/DOWN: LIGHT" %
                               ("RED" if self.display_color == 0 else "COLOR",
                                self.backlight_level * 20), INK, 14)
            text.set_size(176, 150); text.center()
            self._mascot(238)
        elif index == 1:
            panel = self._panel(18, 58, 204, 184)
            value = self._label(panel, "-- mV", SKY_DARK, 20)
            self.page_status = value
            value.set_size(180, 42)
            value.align(lv.ALIGN.TOP_MID, 0, 8)
            log = self._label(panel, "RELEASED\nADC ready", INK, 14)
            log.set_size(180, 105)
            log.set_pos(9, 54)
            self.page_results = log
            self._mascot(238)
        elif index == 2:
            panel = self._panel(18, 62, 204, 168)
            disc_box = self._panel(58, 12, 72, 72, INK, panel)
            disc = self._block(disc_box, 18, 18, 36, 36, RED)
            disc.set_style_radius(lv.RADIUS_CIRCLE, 0)
            text = self._label(panel, "OK: 1kHz TONE\nUP: RECORD + PLAY", INK, 14)
            self.page_status = text
            text.set_size(176, 48); text.align(lv.ALIGN.BOTTOM_MID, 0, -9)
            self._mascot(238)
        elif index == 3:
            panel = self._panel(24, 67, 192, 157, YELLOW)
            soc = self._label(panel, self._battery_text(), INK, 20)
            self.page_status = soc
            soc.set_size(176, 30)
            soc.align(lv.ALIGN.TOP_MID, 0, 18)
            soc.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
            mv = self._label(panel, self._battery_voltage_text(), INK, 14)
            self.page_voltage = mv
            mv.set_size(176, 24)
            mv.align(lv.ALIGN.TOP_MID, 0, 52)
            mv.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
            self._panel(38, 91, 100, 38, GRASS, panel)
            self._mascot(238)
        elif index == 4:
            panel = self._panel(12, 54, 216, 190)
            status = self._label(panel, "Starting Wi-Fi...", SKY_DARK, 14)
            self.page_status = status
            status.set_size(205, 28)
            status.set_pos(2, 2)
            self.page_rows = []
            for row in range(8):
                result = self._label(panel, "", INK, 14)
                result.set_size(205, 16)
                result.set_pos(2, 35 + row * 16)
                self.page_rows.append(result)
            self.page_rows[0].set_text("RSSI  SSID  CHANNEL")
            self._mascot(246)
        elif index == 5:
            panel = self._panel(22, 58, 196, 180)
            text = self._label(panel, "Ready. OK: SCAN", INK, 14)
            self.page_status = text
            text.set_size(168, 30); text.set_pos(14, 66)
            self.page_rows = []
            for row in range(6):
                result = self._label(panel, "", INK, 14)
                result.set_size(168, 16)
                result.set_pos(14, 105 + row * 16)
                self.page_rows.append(result)
            self.page_rows[0].set_text("Press OK to scan")
            self._mascot(244)
        else:
            panel = self._panel(14, 54, 212, 190)
            selected = "LIGHT" if self.low_power_mode == 0 else "DEEP"
            text = self._label(panel, "UP: LIGHT  DOWN: DEEP\nSELECTED: %s  OK: RUN" % selected, INK, 14)
            self.page_status = text
            text.set_size(184, 42); text.align(lv.ALIGN.TOP_MID, 0, 1)
            for i, item in enumerate(("LIGHT SLEEP  |  2 SEC", "DEEP SLEEP   |  5 SEC")):
                card = self._panel(21, 111 + i * 54, 176, 42,
                                   YELLOW if i == self.low_power_mode else PAPER)
                label = self._label(card, item, INK, 14)
                label.set_size(160, 24); label.center()
            self._mascot(246)
        lv.screen_load(root)

    def _start_page_scan(self, index):
        if index == 4 and self.page == "WI-FI SCAN":
            self._wifi_scan()
        elif index == 5 and self.page == "BLUETOOTH LE":
            self._ble_scan()
        else:
            return
        # The scan blocked _poll() for a couple of seconds, so the OK press
        # that opened this page is released while nobody is polling.  Drop the
        # half-finished press state; otherwise the delayed release is timed as
        # a long press and the page closes again immediately.
        self._discard_press()

    def _battery_reading(self):
        try:
            soc_raw = int.from_bytes(self.i2c.readfrom_mem(0x63, 0x04, 2), "big")
            vcell_raw = int.from_bytes(self.i2c.readfrom_mem(0x63, 0x02, 2), "big") & 0x3FFF
            # CW2017 VCELL is 312.5 uV/LSB; keep integer arithmetic on-device.
            mv = (vcell_raw * 3125) // 10000
            soc = max(0, min(100, soc_raw // 256))
            return soc, mv
        except Exception:
            return None, None

    def _battery_text(self):
        soc, _mv = self._battery_reading()
        return "%d%%" % soc if soc is not None else "--%"

    def _battery_voltage_text(self):
        _soc, mv = self._battery_reading()
        return "%d mV" % mv if mv is not None else "-- mV"

    def _refresh_battery_page(self):
        soc, mv = self._battery_reading()
        if self.page != "BATTERY":
            return
        if self.page_status:
            self.page_status.set_text("%d%%" % soc if soc is not None else "--%")
        if self.page_voltage:
            self.page_voltage.set_text("%d mV" % mv if mv is not None else "-- mV")

    def _card(self, parent, text, index, y):
        x = 11 + (index % 2) * 112
        card = self._block(parent, x + 5, y + 6, 102, 40, INK)
        card = self._block(parent, x, y, 102, 40, YELLOW if index == self.selected else PAPER)
        card.set_style_border_color(lv.color_hex(INK), 0)
        card.set_style_border_width(3, 0)
        label = self._label(card, text, INK, 14)
        label.center()
        return card

    def show_home(self):
        self.page = None
        root = self._base("FoloToy")
        for i, item in enumerate(self.ITEMS):
            self._card(root, item, i, 52 + (i // 2) * 47)
        self._mascot(242)

    def show_page(self, name, lines, accent=GRASS):
        self.page = name
        root = self._base(name)
        y = 74
        for line, color in lines:
            label = self._label(root, line, color, 16)
            label.align(lv.ALIGN.TOP_MID, 0, y)
            y += 34
        footer = self._label(root, "HOLD OK TO RETURN", BLUE, 14)
        footer.align(lv.ALIGN.BOTTOM_MID, 0, -14)

    def open_selected(self):
        # Keep every detail page aligned with the reference application's
        # corresponding demo instead of using a generic information layout.
        self._reference_page(self.selected)
        return
        name = self.ITEMS[self.selected]
        if name == "Audio":
            try:
                codec = self.i2c.readfrom_mem(0x18, 0x00, 1)[0]
                detail = "ES8311  READY  0x%02X" % codec
            except Exception:
                detail = "ES8311  NOT FOUND"
            self.show_page("AUDIO", (("Audio workspace", INK), (detail, GRASS),
                                      ("Use I2S + MCLK 4.096MHz", YELLOW),
                                      ("Your app owns playback", BLUE)))
        elif name == "Wi-Fi":
            lines = [("Scanning 2.4 GHz...", YELLOW)]
            try:
                import network
                sta = network.WLAN(network.STA_IF)
                sta.active(True)
                aps = sta.scan()
                lines = [("%d networks found" % len(aps), GRASS)]
                for ap in aps[:4]:
                    ssid = ap[0].decode("utf-8", "replace") or "<hidden>"
                    lines.append(("%s  %ddBm" % (ssid[:13], ap[3]), INK))
            except Exception as exc:
                lines = [("Wi-Fi unavailable", RED), (str(exc)[:25], YELLOW)]
            self.show_page("WI-FI", tuple(lines))
        elif name == "Battery":
            try:
                mv_raw = int.from_bytes(self.i2c.readfrom_mem(0x63, 0x02, 2), "big") & 0x3FFF
                mv = (mv_raw * 3125) // 10000
                soc = self._battery_text()
                lines = [("Battery  " + soc, GRASS), ("Voltage  %dmV" % mv, INK),
                         ("I2C  ES8311 + CW2017", BLUE), ("ST7789  240x320", YELLOW)]
            except Exception:
                lines = [("I2C devices unavailable", RED)]
            self.show_page("BATTERY", tuple(lines))
        else:
            self.show_page(name.upper()[:12], (("Low-power ready", GRASS),
                                      ("ES8311 can be suspended", INK),
                                      ("Press reset to wake", YELLOW)))

    def _release_ble(self):
        """Stop the BLE host so Wi-Fi can allocate its internal buffers.

        The ESP32-C3 has no PSRAM, and a live NimBLE host plus the Wi-Fi
        driver cannot both fit in internal RAM: whichever starts second fails
        with EIO or "WiFi Out of Memory".  Only one radio session is needed at
        a time for these scan pages.
        """
        if self.ble is None:
            return
        try:
            self.ble.gap_scan(None)
        except Exception:
            pass
        try:
            self.ble.active(False)
        except Exception:
            pass
        self.ble = None
        import gc
        gc.collect()

    def _wifi_scan(self):
        if self._wifi_busy:
            return
        self._wifi_busy = True
        self._wifi_pending = False
        self._wifi_error = None
        if self.page_status:
            self.page_status.set_text("Scanning Wi-Fi...")
        try:
            # Free the BLE host first; both radios cannot hold internal RAM.
            self._release_ble()
            # WLAN.scan() must stay in the main MicroPython task.  Calling the
            # ESP32 network driver from _thread can race driver state and
            # reset the chip when entering this page or pressing OK.
            import network
            sta = network.WLAN(network.STA_IF)
            sta.active(True)
            aps = sta.scan()
            rows = []
            for ap in aps:
                ssid = ap[0].decode("utf-8", "replace") or "<hidden>"
                rows.append("%4d  %-12s %2d" % (ap[3], ssid[:12], ap[2]))
            self._wifi_rows = rows
            self._wifi_offset = 0
            self._wifi_error = None
            self._apply_wifi_results()
        except Exception as exc:
            self._wifi_error = str(exc)
            self._apply_wifi_results()
        finally:
            self._wifi_busy = False

    def _apply_wifi_results(self):
        self._wifi_pending = False
        if self.page != "WI-FI SCAN" or not self.page_status:
            return
        if self._wifi_error:
            self.page_status.set_text("Wi-Fi failed: " + self._wifi_error[:18])
            return
        self.page_status.set_text("%d APs  OK:SCAN  UP/DN:PAGE" % len(self._wifi_rows))
        self._render_wifi_results()

    def _render_wifi_results(self):
        if not self.page_rows:
            return
        page_size = len(self.page_rows)
        rows = ["RSSI  SSID  CHANNEL"] + self._wifi_rows
        start = self._wifi_offset
        visible = rows[start:start + page_size]
        for index, label in enumerate(self.page_rows):
            label.set_text(visible[index] if index < len(visible) else "")

    def _ble_irq(self, event, data):
        if event == self._ble_result_event:
            addr_type, addr, adv_type, rssi, adv_data = data
            address = bytes(addr)
            name = self._ble_adv_name(adv_data)
            previous = self._ble_records.get(address)
            # Privacy-addressed advertisements can produce hundreds of
            # callbacks in one scan. Keep a bounded, de-duplicated snapshot so
            # rendering cannot exhaust the ESP32-C3 heap.
            if previous is None and len(self._ble_records) >= 128:
                return
            if previous is None or rssi > previous[0] or (name and not previous[1]):
                self._ble_records[address] = (rssi, name)
        elif event == self._ble_done_event:
            self._ble_done_pending = True

    @staticmethod
    def _ble_adv_name(adv_data):
        """Extract the complete/short local name from BLE AD structures."""
        data = bytes(adv_data)
        offset = 0
        short_name = ""
        while offset + 1 < len(data):
            length = data[offset]
            if length == 0 or offset + length >= len(data):
                break
            ad_type = data[offset + 1]
            payload = data[offset + 2:offset + 1 + length]
            if ad_type in (0x08, 0x09):
                try:
                    name = payload.decode("utf-8").replace("|", "/").strip()
                except Exception:
                    name = ""
                if name:
                    if ad_type == 0x09:
                        return name[:24]
                    short_name = name[:24]
            offset += length + 1
        return short_name

    def _apply_ble_result(self, _arg):
        self._ble_done_pending = False
        if self.page != "BLUETOOTH LE" or not self.page_status:
            return
        results = sorted(self._ble_records.items(),
                         key=lambda item: item[1][0], reverse=True)
        self._ble_rows = []
        for addr, (rssi, name) in results:
            mac = ":".join("%02X" % b for b in addr)
            if name:
                self._ble_rows.append("%s | %s | %ddBm" % (name, mac, rssi))
            else:
                self._ble_rows.append("%s | %ddBm" % (mac, rssi))
        self._ble_offset = 0
        self.page_status.set_text("%d BLE  UP/DN:PAGE" % len(self._ble_rows))
        self._render_ble_results()

    def _render_ble_results(self):
        if not self.page_rows:
            return
        page_size = len(self.page_rows)
        start = self._ble_offset
        visible = self._ble_rows[start:start + page_size]
        if not visible:
            visible = ["No BLE devices"]
        for index, label in enumerate(self.page_rows):
            label.set_text(visible[index] if index < len(visible) else "")

    def _release_wifi(self):
        """Stop the Wi-Fi driver so the BLE host can allocate its RAM."""
        try:
            import network
            sta = network.WLAN(network.STA_IF)
            if sta.active():
                sta.active(False)
        except Exception:
            pass
        import gc
        gc.collect()

    def _ble_scan(self):
        try:
            import bluetooth
            self._ble_result_event = getattr(bluetooth, "_IRQ_SCAN_RESULT", 5)
            self._ble_done_event = getattr(bluetooth, "_IRQ_SCAN_DONE", 6)
            # Free the Wi-Fi driver first; both radios cannot hold internal RAM.
            self._release_wifi()
            if self.ble is None:
                self.ble = bluetooth.BLE()
            else:
                try:
                    self.ble.gap_scan(None)
                except Exception:
                    pass
            try:
                self.ble.active(True)
                self.ble.irq(self._ble_irq)
            except OSError:
                # NimBLE can retain a previous host after a failed scan.
                # Recreate the host once instead of leaving the page at EIO.
                self.ble = bluetooth.BLE()
                self.ble.active(True)
                self.ble.irq(self._ble_irq)
            self.ble_results = []
            self._ble_records = {}
            self._ble_last_render_ms = time.ticks_ms()
            self.page_status.set_text("Scanning BLE...")
            # Three seconds is enough for normal advertising intervals while
            # keeping the page responsive; partial results are rendered live.
            self.ble.gap_scan(3000, 30000, 30000, True)
        except Exception as exc:
            if self.page_status:
                self.page_status.set_text("BLE failed: " + str(exc)[:18])

    def _audio_play(self):
        if self.audio_busy:
            return
        self.audio_busy = True
        try:
            _thread.start_new_thread(self._audio_tone_worker, ())
        except Exception as exc:
            self.audio_busy = False
            if self.page_status:
                self.page_status.set_text("AUDIO FAILED: " + str(exc)[:18])

    def _audio_tone_worker(self):
        codec = None
        i2s = None
        try:
            from es8311 import ES8311
            codec = ES8311(self.i2c)
            codec.configure_slave(16000, 16)
            codec.mute(False)
            i2s = I2S(0, sck=Pin(5), ws=Pin(3), sd=Pin(2), mck=Pin(6),
                      mode=I2S.TX, bits=16, format=I2S.MONO,
                      rate=16000, ibuf=2048)
            self._queue_audio_status("PLAYING 1kHz...")
            # Stream a small repeating chunk instead of allocating a full
            # second of PCM, which can fail with ENOMEM beside LVGL buffers.
            sample = bytearray(1024)
            for i in range(0, len(sample), 2):
                value = 7000 if ((i // 2) % 16) < 8 else -7000
                sample[i] = value & 0xFF
                sample[i + 1] = (value >> 8) & 0xFF
            for _ in range(32):
                i2s.write(sample)
            self._queue_audio_status("DONE: 1kHz TONE")
        except Exception as exc:
            self._queue_audio_status("AUDIO FAILED: " + str(exc)[:18])
        finally:
            if i2s is not None:
                try:
                    i2s.deinit()
                except Exception:
                    pass
            if codec is not None:
                try:
                    codec.mute(True); codec.sleep()
                except Exception:
                    pass
            self.audio_busy = False

    def _queue_audio_status(self, text):
        self._audio_status_pending = text
        try:
            micropython.schedule(self._apply_audio_status, 0)
        except RuntimeError:
            pass

    def _apply_audio_status(self, _arg):
        text = self._audio_status_pending
        self._audio_status_pending = None
        if self.page == "AUDIO" and self.page_status and text:
            self.page_status.set_text(text)

    def _audio_record_play(self):
        """Capture a short PCM clip and play it back without blocking LVGL."""
        import gc
        sample_rate = 16_000
        target = sample_rate * 2 * 2  # two seconds, mono, 16-bit
        chunk = 1024
        gc.collect()
        pcm = bytearray(target)
        offset = 0
        codec = None
        i2s = None
        try:
            from es8311 import ES8311
            self._queue_audio_status("RECORDING 2 SEC...")
            codec = ES8311(self.i2c)
            codec.configure_slave(sample_rate, 16)
            codec.mute(False)
            i2s = I2S(0, sck=Pin(5), ws=Pin(3), sd=Pin(4), mck=Pin(6),
                      mode=I2S.RX, bits=16, format=I2S.MONO,
                      rate=sample_rate, ibuf=4096)
            while offset < target:
                count = i2s.readinto(memoryview(pcm)[offset:offset + chunk])
                if count:
                    offset += min(count, target - offset)
            i2s.deinit(); i2s = None
            codec.mute(True); codec.sleep(); codec = None
            time.sleep_ms(100)

            self._queue_audio_status("PLAYING RECORDING...")
            codec = ES8311(self.i2c)
            codec.configure_slave(sample_rate, 16)
            codec.mute(False)
            i2s = I2S(0, sck=Pin(5), ws=Pin(3), sd=Pin(2), mck=Pin(6),
                      mode=I2S.TX, bits=16, format=I2S.MONO,
                      rate=sample_rate, ibuf=4096)
            offset = 0
            while offset < target:
                sent = i2s.write(memoryview(pcm)[offset:offset + chunk])
                if not sent:
                    break
                offset += sent
            self._queue_audio_status("DONE: RECORD + PLAY")
        except Exception as exc:
            self._queue_audio_status("AUDIO FAILED: " + str(exc)[:18])
        finally:
            if i2s is not None:
                try:
                    i2s.deinit()
                except Exception:
                    pass
            if codec is not None:
                try:
                    codec.mute(True); codec.sleep()
                except Exception:
                    pass
            self.audio_busy = False

    def _page_key(self, key):
        if self.page == "DISPLAY":
            if key == 3:
                self.display_color = (self.display_color + 1) % 5
                # Rebuild the reference card so the selected color is visible.
                self._reference_page(0)
            elif key in (1, 2):
                self.backlight_level = max(1, min(5, self.backlight_level +
                                                  (1 if key == 1 else -1)))
                self.backlight.duty_u16(self._backlight_duty[self.backlight_level - 1])
                self._reference_page(0)
        elif self.page == "BUTTON / ADC":
            if self.page_status:
                self.page_status.set_text("%d mV" % (self.adc.read_uv() // 1000))
        elif self.page == "AUDIO":
            if key == 1 and not self.audio_busy:
                self.audio_busy = True
                try:
                    _thread.start_new_thread(self._audio_record_play, ())
                except Exception as exc:
                    self.audio_busy = False
                    self.page_status.set_text("AUDIO FAILED: " + str(exc)[:18])
            elif key == 3:
                self._audio_play()
        elif self.page == "BATTERY":
            self._refresh_battery_page()
        elif self.page == "WI-FI SCAN" and key in (1, 2):
            page_size = len(self.page_rows)
            limit = max(0, len(self._wifi_rows))
            self._wifi_offset = max(0, min(self._wifi_offset + (page_size if key == 2 else -page_size), limit))
            self._render_wifi_results()
        elif self.page == "BLUETOOTH LE" and key in (1, 2):
            page_size = len(self.page_rows)
            limit = max(0, len(self._ble_rows))
            self._ble_offset = max(0, min(self._ble_offset + (page_size if key == 2 else -page_size), limit))
            self._render_ble_results()
        elif self.page == "WI-FI SCAN" and key == 3:
            self._wifi_scan()
            self._discard_press()
        elif self.page == "BLUETOOTH LE" and key == 3:
            self._ble_scan()
            self._discard_press()
        elif self.page == "LOW POWER" and key in (1, 2):
            self._set_low_power_mode(0 if key == 1 else 1)
        elif self.page == "LOW POWER" and key == 3:
            try:
                import machine
                if self.low_power_mode == 0:
                    self.page_status.set_text("LIGHT SLEEP: 2 SEC")
                    self._prepare_sleep_peripherals()
                    machine.lightsleep(2000)
                    self._wake_sleep_peripherals()
                    self.page_status.set_text("LIGHT WAKE: TIMER")
                else:
                    self.page_status.set_text("DEEP SLEEP: 5 SEC")
                    self._prepare_sleep_peripherals()
                    machine.deepsleep(5000)
            except Exception as exc:
                if self.page_status:
                    self.page_status.set_text("sleep failed: " + str(exc)[:16])

    def _prepare_sleep_peripherals(self):
        """Stop software-controlled peripherals before a sleep transition."""
        if self.ble is not None:
            try:
                self.ble.gap_scan(None)
            except Exception:
                pass
        try:
            import network
            network.WLAN(network.STA_IF).active(False)
        except Exception:
            pass
        try:
            from es8311 import ES8311
            ES8311(self.i2c).sleep()
        except Exception:
            pass
        try:
            self.display.panel.sleep()
        except Exception:
            pass
        self.backlight.duty_u16(0)

    def _wake_sleep_peripherals(self):
        try:
            self.display.panel.wake()
        except Exception:
            pass
        self.backlight.duty_u16(self._backlight_duty[self.backlight_level - 1])

    def _set_low_power_mode(self, mode):
        self.low_power_mode = mode
        self._reference_page(6)

    def _key(self):
        value = self.adc.read_uv() // 1000 if hasattr(self.adc, "read_uv") else self.adc.read()
        self.last_mv = value
        # Keep these half-open windows identical to BSP_BTN_MV_TABLE in the
        # AI Passport project: UP=0 ohm, DOWN=1 kohm, OK=2.2 kohm.
        if value < 150:
            return 1
        if value < 447:
            return 2
        if value < 1900:
            return 3
        return 0

    def _poll(self, _timer):
        key = self._key()
        now = time.ticks_ms()
        if self._wifi_pending:
            self._apply_wifi_results()
        if self._ble_done_pending:
            self._apply_ble_result(None)
        if self.page == "BLUETOOTH LE" and self._ble_records and time.ticks_diff(
                now, self._ble_last_render_ms) >= 500:
            self._ble_last_render_ms = now
            self._apply_ble_result(None)
        if self.page == "BUTTON / ADC" and self.page_status:
            names = ("RELEASED", "UP", "DOWN", "OK")
            self.page_status.set_text("%s\n%d mV" % (names[key], self.last_mv))
        if self.page == "BATTERY" and time.ticks_diff(now, self.last_battery_ms) >= 1000:
            self.last_battery_ms = now
            self._refresh_battery_page()
        if key != self.last_key:
            if key:
                self._button_event(key, "PRESS")
            elif self.last_key:
                self._button_event(self.last_key, "RELEASE")
        if key == 3 and self.last_key != 3:
            self.down_since = now
            self.long_sent = False
        if key == 3 and self.down_since is not None and not self.long_sent:
            if time.ticks_diff(now, self.down_since) >= 800:
                self.long_sent = True
                self._button_event(3, "LONG")
        if key != 3 and self.last_key == 3 and self.down_since is not None:
            held = time.ticks_diff(now, self.down_since)
            self.down_since = None
            if self.page is not None and held >= 800:
                self.show_home()
            elif self.page is None and held < 800:
                self.open_selected()
            elif self.page is not None and held < 800:
                self._page_key(3)
        elif key == 1 and self.last_key != 1 and self.page is None:
            self.selected = (self.selected - 1) % len(self.ITEMS)
            self.show_home()
        elif key == 2 and self.last_key != 2 and self.page is None:
            self.selected = (self.selected + 1) % len(self.ITEMS)
            self.show_home()
        elif self.page is not None and key in (1, 2) and self.last_key != key:
            self._page_key(key)
        self.last_key = key

    def _button_event(self, key, event):
        names = ("", "UP", "DOWN", "OK")
        line = "%s: %s" % (names[key], event)
        self.button_log.append(line)
        if len(self.button_log) > 4:
            self.button_log.pop(0)
        if self.page == "BUTTON / ADC":
            if self.page_status:
                state = "RELEASED" if event == "RELEASE" else names[key]
                self.page_status.set_text("%s\n%d mV" % (state, self.last_mv))
            if self.page_results:
                self.page_results.set_text("\n".join(self.button_log))


app = PassportApp()
print("AI Passport app ready: UP/DOWN browse, OK open, hold OK return")
