#define MICROPY_HW_BOARD_NAME               "FoloToy AI Passport"
#define MICROPY_HW_MCU_NAME                 "ESP32-C3"

// Mount the user filesystem before boot.py/main.py are evaluated.  The normal
// startup order then prefers a user-uploaded /main.py and falls back to the
// frozen example when no user file exists.
#define MICROPY_BOARD_FROZEN_BOOT_FILE      "ai_passport_boot.py"

// The board uses the native USB Serial/JTAG interface on GPIO18/19 for the
// MicroPython REPL.  Define MICROPY_HW_ENABLE_UART_REPL in a local build when
// an external UART adapter is preferred.

// Shared I2C0 bus: ES8311 codec (0x18) and CW2017 fuel gauge (0x63).
#define MICROPY_HW_I2C0_SCL                 (7)
#define MICROPY_HW_I2C0_SDA                 (10)

// LCD ST7789P3 uses MicroPython SPI(1), which maps to ESP-IDF SPI2 on ESP32-C3.
#define MICROPY_HW_SPI1_SCK                 (8)
#define MICROPY_HW_SPI1_MOSI                (9)
#define MICROPY_HW_SPI1_MISO                (-1)
