ARDUINO_DIR := /usr/share/arduino
ARDMK_DIR   := /usr/share/arduino
AVR_TOOLS_DIR := /usr
USER_LIB_PATH := libraries

BOARD_TAG    = atmega328
MONITOR_PORT = /dev/ttyUSB*
ARDUINO_LIBS = SPI libgfx

CFLAGS += -Wall
EXTRA_CFLAGS += -std=c99

include /usr/share/arduino/Arduino.mk

