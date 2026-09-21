"""Small LVGL v9 event loop for MicroPython boards."""

import micropython
import lvgl as lv
from machine import Timer


class event_loop:
    _instance = None

    def __init__(self, freq=50, timer_id=0):
        if event_loop._instance is not None:
            raise RuntimeError("LVGL event loop is already running")
        if not lv.is_initialized():
            lv.init()
        self.period = max(1, 1000 // freq)
        self.timer = Timer(timer_id)
        # Keep a stable callback object.  Creating a bound method on every
        # timer interrupt can leave the scheduled callback without a live
        # Python object when the GC runs.
        self._handler_ref = self._run
        self.timer.init(mode=Timer.PERIODIC, period=self.period,
                        callback=self._timer_cb)
        event_loop._instance = self

    @classmethod
    def is_running(cls):
        return cls._instance is not None

    def _run(self, _):
        try:
            lv.timer_handler()
        except Exception as exc:
            print("LVGL task error:", exc)

    def _timer_cb(self, _):
        lv.tick_inc(self.period)
        try:
            micropython.schedule(self._handler_ref, 0)
        except RuntimeError:
            # A scheduled callback is already pending; the next tick retries.
            pass

    def deinit(self):
        self.timer.deinit()
        event_loop._instance = None
