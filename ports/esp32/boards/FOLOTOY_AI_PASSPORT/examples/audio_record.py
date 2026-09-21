from machine import I2S, Pin
from es8311 import ES8311

codec = ES8311()
codec.configure_slave(sample_rate=16000, bits=16)

i2s = I2S(0, sck=Pin(5), ws=Pin(3), sd=Pin(4), mck=Pin(6),
          mode=I2S.RX, bits=16, format=I2S.MONO, rate=16000, ibuf=4096)
buf = bytearray(512)
i2s.readinto(buf)
print("captured", len(buf), "bytes")
i2s.deinit()
codec.sleep()
