from machine import I2S, Pin
from es8311 import ES8311

codec = ES8311()
codec.configure_slave(sample_rate=16000, bits=16)

i2s = I2S(0, sck=Pin(5), ws=Pin(3), sd=Pin(2), mck=Pin(6),
          mode=I2S.TX, bits=16, format=I2S.MONO, rate=16000, ibuf=4096)
silence = bytes(512)
for _ in range(100):
    i2s.write(silence)
i2s.deinit()
codec.sleep()
print("ES8311 playback path test complete")
