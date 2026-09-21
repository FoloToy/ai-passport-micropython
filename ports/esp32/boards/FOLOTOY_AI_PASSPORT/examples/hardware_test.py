"""FoloToy AI Passport end-to-end hardware checkout.

Run ``import hardware_test`` from the USB REPL.  The test is deliberately
serial-first: every step prints PASS/FAIL and the display is exercised with
solid RGB565 patterns.  It does not write battery profiles or enter sleep.
"""

from machine import ADC, I2C, I2S, Pin, SPI
import time

from es8311 import ES8311
from st7789 import ST7789

RESULTS = []
WIFI_NETWORKS = []


def report(name, ok, detail=""):
    RESULTS.append((name, bool(ok)))
    print("[%s] %-12s %s" % ("PASS" if ok else "FAIL", name, detail))
    return ok


def test_i2c():
    bus = I2C(0, scl=Pin(7), sda=Pin(10), freq=400_000)
    found = bus.scan()
    report("I2C scan", 0x18 in found and 0x63 in found,
           "found=" + repr([hex(x) for x in found]))
    return bus


def test_battery(bus):
    try:
        version = bus.readfrom_mem(0x63, 0x00, 1)[0]
        vcell = int.from_bytes(bus.readfrom_mem(0x63, 0x02, 2), "big") & 0x3FFF
        soc_raw = int.from_bytes(bus.readfrom_mem(0x63, 0x04, 2), "big")
        config = bus.readfrom_mem(0x63, 0x08, 1)[0]
        # CW2017 voltage is raw * 312.5 uV; SOC uses 8 fractional bits.
        mv = (vcell * 3125) // 10_000
        soc = soc_raw / 256
        ok = version != 0xFF and config != 0xFF and 0 <= soc <= 100.5
        report("CW2017", ok,
               "ver=0x%02x voltage=%dmV soc=%.1f%% cfg=0x%02x" %
               (version, mv, soc, config))
    except Exception as exc:
        report("CW2017", False, repr(exc))


def test_buttons():
    adc = ADC(Pin(0))
    adc.atten(ADC.ATTN_11DB)
    def read_mv():
        values = []
        for _ in range(4):
            values.append(adc.read_uv() // 1000 if hasattr(adc, "read_uv") else adc.read())
            time.sleep_ms(5)
        return sum(values) // len(values)

    idle = read_mv()
    report("BUTTON idle", idle >= 1900, "GPIO0=%dmV" % idle)
    # The three resistor windows are 0-150, 150-447 and 447-1900 mV.
    for index, (low, high) in enumerate(((0, 150), (150, 447), (447, 1900)), 1):
        print("Press button %d within 2 seconds..." % index)
        deadline = time.ticks_add(time.ticks_ms(), 2000)
        seen = False
        value = idle
        while time.ticks_diff(deadline, time.ticks_ms()) > 0:
            value = read_mv()
            if low <= value < high:
                seen = True
                break
        report("BUTTON %d" % index, seen, "GPIO0=%dmV expected=%d..%d" %
               (value, low, high))


def test_display():
    spi = SPI(1, baudrate=80_000_000, polarity=0, phase=0,
              sck=Pin(8), mosi=Pin(9), miso=None)
    lcd = ST7789(spi=spi)
    for color in (0xF800, 0x07E0, 0x001F, 0x0000):
        lcd.fill(color)
        time.sleep_ms(250)
    report("ST7789", True, "240x320 SPI1 80MHz; RGB test pattern shown")
    return lcd


def test_codec_and_audio():
    codec = ES8311()
    codec.configure_slave()
    regs = codec.check()
    codec_ok = regs[0x00] == 0x80 and regs[0x01] == 0x3F and regs[0x45] == 0x00
    report("ES8311", codec_ok, "regs=" + repr({hex(k): hex(v) for k, v in regs.items()}))

    rx = I2S(0, sck=Pin(5), ws=Pin(3), sd=Pin(4), mck=Pin(6), mode=I2S.RX,
             bits=16, format=I2S.MONO, rate=16_000, ibuf=8192)
    sample = bytearray(4096)
    captured = rx.readinto(sample)
    rx.deinit()
    if captured is None:
        captured = 0
    report("I2S capture", captured > 0, "bytes=%d" % captured)

    tx = I2S(0, sck=Pin(5), ws=Pin(3), sd=Pin(2), mck=Pin(6), mode=I2S.TX,
             bits=16, format=I2S.MONO, rate=16_000, ibuf=8192)
    played = tx.write(memoryview(sample)[:captured]) if captured else 0
    tx.deinit()
    report("I2S playback", played == captured, "bytes=%d" % played)
    codec.sleep()


def test_wifi():
    WIFI_NETWORKS.clear()
    try:
        import network
        sta = network.WLAN(network.STA_IF)
        sta.active(True)
        aps = sta.scan()
        for ap in aps:
            ssid = ap[0].decode("utf-8", "replace") or "<hidden>"
            WIFI_NETWORKS.append((ssid[:12], ap[3], ap[2]))
        report("Wi-Fi scan", True, "2.4GHz APs=%d" % len(aps))
        sta.active(False)
    except Exception as exc:
        report("Wi-Fi scan", False, repr(exc))


def run():
    RESULTS.clear()
    print("\nFoloToy AI Passport hardware test")
    print("Do not press reset or disconnect USB during the audio step.\n")
    bus = test_i2c()
    test_battery(bus)
    test_buttons()
    test_display()
    test_codec_and_audio()
    test_wifi()
    print("\nHardware test complete. Review PASS/FAIL lines above.")


if __name__ == "__main__":
    run()
