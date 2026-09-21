# Build the official LVGL MicroPython binding into this board variant.
list(APPEND USER_C_MODULES
    ${CMAKE_CURRENT_LIST_DIR}/../../../../user_modules/lv_binding_micropython/micropython.cmake)

# Freeze the board's LVGL adapter and smoke/demo modules so they work with the
# minimal partition layout, which intentionally does not reserve a filesystem.
set(MICROPY_FROZEN_MANIFEST ${MICROPY_BOARD_DIR}/manifest.py)

include(boards/mpconfigboard_esp32c3_common.cmake)

list(APPEND SDKCONFIG_DEFAULTS
    boards/sdkconfig.flash_qio_80m
    ${MICROPY_BOARD_DIR}/sdkconfig.board
)
