"""AI Passport boot hook: run the bundled app only without a user main.py."""

import gc
import vfs
from flashbdev import bdev

try:
    if bdev:
        vfs.mount(bdev, "/")
except OSError:
    import inisetup

    inisetup.setup()

try:
    import os

    os.stat("/main.py")
except OSError:
    import ai_passport_app

gc.collect()
