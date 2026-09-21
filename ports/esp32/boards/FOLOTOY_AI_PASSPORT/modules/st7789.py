"""Small ST7789P3 driver for the FoloToy AI Passport (RGB565)."""

from machine import Pin, SPI
import time


class ST7789:
    _FONT = {
        " ": (0, 0, 0, 0, 0), "-": (4, 4, 4, 4, 4), ">": (0x20, 0x10, 8, 0x10, 0x20),
        ":": (0, 0x14, 0, 0x14, 0),
        "0": (0x1E, 0x21, 0x25, 0x21, 0x1E), "1": (0, 0x22, 0x3F, 0x20, 0),
        "2": (0x32, 0x29, 0x29, 0x29, 0x26), "3": (0x12, 0x21, 0x29, 0x29, 0x16),
        "4": (0x0C, 0x0A, 0x09, 0x3F, 0x08), "5": (0x2F, 0x29, 0x29, 0x29, 0x19),
        "6": (0x1E, 0x29, 0x29, 0x29, 0x10), "7": (1, 1, 0x31, 9, 7),
        "8": (0x16, 0x29, 0x29, 0x29, 0x16), "9": (6, 9, 9, 9, 0x3E),
        "A": (0x3E, 9, 9, 9, 0x3E), "B": (0x3F, 0x25, 0x25, 0x25, 0x1A),
        "C": (0x1E, 0x21, 0x21, 0x21, 0x12), "D": (0x3F, 0x21, 0x21, 0x12, 0x0C),
        "E": (0x3F, 0x25, 0x25, 0x25, 0x21), "F": (0x3F, 5, 5, 5, 1),
        "G": (0x1E, 0x21, 0x29, 0x29, 0x1A), "H": (0x3F, 4, 4, 4, 0x3F),
        "I": (0x21, 0x21, 0x3F, 0x21, 0x21), "J": (0x10, 0x20, 0x21, 0x1F, 1),
        "K": (0x3F, 4, 0x0A, 0x11, 0x20), "L": (0x3F, 0x20, 0x20, 0x20, 0x20),
        "M": (0x3F, 2, 4, 2, 0x3F), "N": (0x3F, 2, 4, 8, 0x3F),
        "O": (0x1E, 0x21, 0x21, 0x21, 0x1E), "P": (0x3F, 9, 9, 9, 6),
        "Q": (0x1E, 0x21, 0x31, 0x21, 0x5E), "R": (0x3F, 9, 0x19, 0x29, 0x26),
        "S": (0x26, 0x29, 0x29, 0x29, 0x12), "T": (1, 1, 0x3F, 1, 1),
        "U": (0x1F, 0x20, 0x20, 0x20, 0x1F), "V": (7, 8, 0x30, 8, 7),
        "W": (0x1F, 0x20, 0x18, 0x20, 0x1F), "X": (0x33, 0x0C, 4, 0x0C, 0x33),
        "Y": (3, 4, 0x38, 4, 3), "Z": (0x31, 0x29, 0x25, 0x23, 0x21),
    }
    def __init__(self, spi=None, width=240, height=320, cs=1, dc=20, bl=21):
        self.width = width
        self.height = height
        self.spi = spi or SPI(1, baudrate=80_000_000, polarity=0, phase=0,
                              sck=Pin(8), mosi=Pin(9), miso=None)
        self.cs = Pin(cs, Pin.OUT, value=1)
        self.dc = Pin(dc, Pin.OUT, value=1)
        self.bl = Pin(bl, Pin.OUT, value=0)
        self._reset()
        self._init_display()
        self.bl.value(1)

    def _write(self, command, data=b""):
        self.cs.value(0)
        self.dc.value(0)
        self.spi.write(bytes((command,)))
        if data:
            self.dc.value(1)
            self.spi.write(data)
        self.cs.value(1)

    def _reset(self):
        self._write(0x01)
        time.sleep_ms(120)

    def _init_display(self):
        self._write(0x11)
        time.sleep_ms(120)
        self._write(0x3A, b"\x55")       # RGB565
        self._write(0x36, b"\x00")       # portrait, RGB order
        self._write(0x21)                 # inversion on
        self._write(0x13)
        self._write(0x29)
        time.sleep_ms(20)

    def _window(self, x0, y0, x1, y1):
        self._write(0x2A, bytes((x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF)))
        self._write(0x2B, bytes((y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF)))
        self._write(0x2C)

    def fill(self, color):
        self._window(0, 0, self.width - 1, self.height - 1)
        line = bytes((color >> 8, color & 0xFF)) * self.width
        self.cs.value(0)
        self.dc.value(1)
        for _ in range(self.height):
            self.spi.write(line)
        self.cs.value(1)

    def blit(self, pixels, x=0, y=0, width=None, height=None):
        """Write an RGB565 buffer; pixels must be exactly width*height*2 bytes."""
        width = width or self.width
        height = height or self.height
        if len(pixels) != width * height * 2:
            raise ValueError("RGB565 buffer size does not match dimensions")
        self._window(x, y, x + width - 1, y + height - 1)
        self.cs.value(0)
        self.dc.value(1)
        self.spi.write(pixels)
        self.cs.value(1)

    def fill_rect(self, x, y, width, height, color):
        """Fill a small RGB565 rectangle without requiring a framebuffer."""
        self._window(x, y, x + width - 1, y + height - 1)
        line = bytes((color >> 8, color & 0xFF)) * width
        self.cs.value(0)
        self.dc.value(1)
        for _ in range(height):
            self.spi.write(line)
        self.cs.value(1)

    def text(self, message, x, y, color=0xFFFF, scale=2, background=None):
        """Render the built-in 5x7 ASCII subset used by the hardware menu."""
        for char in str(message).upper():
            glyph = self._FONT.get(char, self._FONT["-"])
            width = 6 * scale
            height = 7 * scale
            pixels = bytearray(width * height * 2)
            hi, lo = color >> 8, color & 0xFF
            if background is not None:
                bhi, blo = background >> 8, background & 0xFF
                for pos in range(0, len(pixels), 2):
                    pixels[pos] = bhi
                    pixels[pos + 1] = blo
            for column, bits in enumerate(glyph):
                for row in range(7):
                    if bits & (1 << row):
                        for dx in range(scale):
                            for dy in range(scale):
                                pos = ((row * scale + dy) * width +
                                       column * scale + dx) * 2
                                pixels[pos] = hi
                                pixels[pos + 1] = lo
            self.blit(pixels, x, y, width, height)
            x += 6 * scale

    def sleep(self):
        self.bl.value(0)
        self._write(0x28)
        self._write(0x10)

    def wake(self):
        self._write(0x11)
        time.sleep_ms(120)
        self._write(0x29)
        self.bl.value(1)
