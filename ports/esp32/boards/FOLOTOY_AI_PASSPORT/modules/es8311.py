"""Low-level ES8311 register helper and conservative slave-mode setup."""

from machine import I2C
import time


class ES8311:
    ADDRESS = 0x18

    def __init__(self, i2c=None, address=ADDRESS):
        self.i2c = i2c or I2C(0, scl=7, sda=10, freq=400_000)
        self.address = address

    def write_reg(self, reg, value):
        self.i2c.writeto_mem(self.address, reg, bytes((value & 0xFF,)))

    def read_reg(self, reg):
        return self.i2c.readfrom_mem(self.address, reg, 1)[0]

    def reset(self):
        self.write_reg(0x00, 0x1F)
        time.sleep_ms(5)

    def configure_slave(self, sample_rate=16000, bits=16):
        """Configure the codec for external MCLK/BCLK/WS in slave mode.

        The caller must provide MCLK on GPIO6 and matching I2S timing.  The
        clock divider values below are the common 4.096 MHz / 16 kHz setup
        (256 * fs); use the ESP-ADF coefficient table for other combinations.
        """
        if sample_rate != 16000 or bits != 16:
            raise ValueError("example supports 4.096MHz MCLK, 16kHz, 16-bit")
        self.reset()
        # Match the ESP-ADF open/start sequence before programming the sample
        # rate. REG00=0x80 leaves reset and selects external-clock slave mode.
        for reg, value in ((0x44, 0x08), (0x01, 0x30), (0x02, 0x00),
                           (0x03, 0x10), (0x16, 0x24), (0x04, 0x10),
                           (0x05, 0x00), (0x0B, 0x00), (0x0C, 0x00),
                           (0x10, 0x1F), (0x11, 0x7F), (0x00, 0x80),
                           (0x01, 0x3F), (0x13, 0x10), (0x1B, 0x0A),
                           (0x1C, 0x6A)):
            self.write_reg(reg, value)
        # 4.096 MHz MCLK -> 16 kHz LRCK, BCLK divider 4.
        for reg, value in ((0x02, 0x00), (0x05, 0x00), (0x03, 0x10),
                           (0x04, 0x10), (0x07, 0x00), (0x08, 0xFF),
                           (0x06, 0x03)):
            self.write_reg(reg, value)
        # Philips I2S, 16-bit samples, ADC and DAC paths enabled.
        self.write_reg(0x09, 0x0C)
        self.write_reg(0x0A, 0x0C)
        self.write_reg(0x17, 0xBF)
        self.write_reg(0x0E, 0x02)
        self.write_reg(0x12, 0x00)
        self.write_reg(0x14, 0x1A)
        self.write_reg(0x0D, 0x01)
        self.write_reg(0x15, 0x40)
        self.write_reg(0x37, 0x08)
        self.write_reg(0x45, 0x00)
        self.write_reg(0x32, 0xC0)

    def mute(self, enabled=True):
        value = self.read_reg(0x31) & 0x9F
        self.write_reg(0x31, value | 0x60 if enabled else value)

    def sleep(self):
        for reg, value in ((0x32, 0x00), (0x17, 0x00), (0x0E, 0xFF),
                           (0x12, 0x02), (0x14, 0x00), (0x0D, 0xFA),
                           (0x15, 0x00), (0x02, 0x10), (0x00, 0x00),
                           (0x00, 0x1F), (0x01, 0x30), (0x01, 0x00),
                           (0x45, 0x01), (0x0D, 0xFC), (0x02, 0x00)):
            self.write_reg(reg, value)

    def check(self):
        return {reg: self.read_reg(reg) for reg in (0x00, 0x01, 0x0D, 0x0E, 0x12, 0x45)}
