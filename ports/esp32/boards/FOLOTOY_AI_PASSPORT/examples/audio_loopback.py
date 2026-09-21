"""Record five seconds from ES8311, play it back, and repeat forever.

Copy ``modules/es8311.py`` to the device before running this example.  Audio
is staged in a file instead of a large RAM buffer because 5 seconds of 16 kHz
mono/16-bit PCM is about 160 KiB.
"""

from machine import I2S, Pin
import time
from es8311 import ES8311


SAMPLE_RATE = 16000
RECORD_SECONDS = 5
BYTES_PER_SAMPLE = 2
TARGET_BYTES = SAMPLE_RATE * RECORD_SECONDS * BYTES_PER_SAMPLE
CHUNK_BYTES = 1024
PCM_FILE = "loopback.pcm"

MCLK = Pin(6)
SCK = Pin(5)
WS = Pin(3)
MIC_DATA = Pin(4)
SPK_DATA = Pin(2)


def make_codec():
    codec = ES8311()
    codec.configure_slave(sample_rate=SAMPLE_RATE, bits=16)
    codec.mute(False)
    return codec


def record_once():
    codec = make_codec()
    i2s = I2S(0, sck=SCK, ws=WS, sd=MIC_DATA, mck=MCLK,
              mode=I2S.RX, bits=16, format=I2S.MONO,
              rate=SAMPLE_RATE, ibuf=4096)
    buf = bytearray(CHUNK_BYTES)
    total = 0
    try:
        with open(PCM_FILE, "wb") as pcm:
            while total < TARGET_BYTES:
                count = i2s.readinto(buf)
                if count:
                    remaining = TARGET_BYTES - total
                    pcm.write(buf[:min(count, remaining)])
                    total += min(count, remaining)
        print("recorded", total, "bytes")
    finally:
        i2s.deinit()
        codec.mute(True)
        codec.sleep()


def play_once():
    codec = make_codec()
    i2s = I2S(0, sck=SCK, ws=WS, sd=SPK_DATA, mck=MCLK,
              mode=I2S.TX, bits=16, format=I2S.MONO,
              rate=SAMPLE_RATE, ibuf=4096)
    buf = bytearray(CHUNK_BYTES)
    total = 0
    try:
        with open(PCM_FILE, "rb") as pcm:
            while True:
                count = pcm.readinto(buf)
                if not count:
                    break
                sent = i2s.write(memoryview(buf)[:count])
                total += sent
        print("played", total, "bytes")
    finally:
        i2s.deinit()
        codec.mute(True)
        codec.sleep()


try:
    while True:
        print("recording for", RECORD_SECONDS, "seconds...")
        record_once()
        time.sleep_ms(100)
        print("playing...")
        play_once()
        time.sleep_ms(300)
except KeyboardInterrupt:
    print("loopback stopped")
