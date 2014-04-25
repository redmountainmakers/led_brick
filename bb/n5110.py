#!/usr/bin/python
from time import sleep
import Adafruit_BBIO.GPIO as GPIO
from Adafruit_BBIO.SPI import SPI

# for SPI(0,0):
# Gnd = P9_1
# Light = P9_25 (to taste)
# Vcc = P9_3
# CLK = P9_22
# DIN = P9_18
# DC = P9_24 (to taste)
# CE = P9_17
# RST = P9_23 (to taste)

class n5110:
	def __init__(self, spi = SPI(0,0), gpio_nrst = 'P9_23', gpio_dc = 'P9_24', gpio_nled = 'P9_25'):
		self.gpio_nrst = gpio_nrst
		self.gpio_dc = gpio_dc
		self.gpio_nled = gpio_nled

		self.spi = spi
		self.spi.msh = 4000000
		self.spi.mode = 0b00
		self.spi.bpw = 8
		self.spi.lsbfirst = False
		self.spi.threewire = False
		self.spi.cshigh = False

		GPIO.setup(self.gpio_nrst, GPIO.OUT, initial = GPIO.LOW)
		sleep(0.1) # workaround until library waits for permissions
		GPIO.setup(self.gpio_nrst, GPIO.OUT, initial = GPIO.LOW)
		GPIO.output(self.gpio_nrst, GPIO.LOW) # Reset.

		GPIO.setup(self.gpio_dc, GPIO.OUT, initial = GPIO.LOW)
		sleep(0.1)
		GPIO.setup(self.gpio_dc, GPIO.OUT, initial = GPIO.LOW)
		GPIO.output(self.gpio_dc, GPIO.LOW) # Command.

		if self.gpio_nled:
			GPIO.setup(self.gpio_nled, GPIO.OUT, initial = GPIO.HIGH)
			sleep(0.1)
			GPIO.setup(self.gpio_nled, GPIO.OUT, initial = GPIO.HIGH)
			GPIO.output(self.gpio_nled, GPIO.HIGH) # Off.

		self.reset()

	def _cmdMode(self, enable = True):
		GPIO.output(self.gpio_dc, GPIO.LOW if enable else GPIO.HIGH)

	def backlight(self, enable = True):
		if self.gpio_nled:
			GPIO.output(self.gpio_nled, GPIO.LOW if enable else GPIO.HIGH)

	def _cmdNOP(self):
		self.spi.writebytes([0])

	def _cmdFunctionSet(self, cmdSet = 0, verticalAddr = False, powerDown = False):
		cmd = 0b00100000
		if cmdSet: cmd |= 1 << 0
		if verticalAddr: cmd |= 1 << 1
		if powerDown: cmd |= 1 << 2
		self.spi.writebytes([cmd])

	def _cmd0setDisplayControl(self, inverse = False, enable = True):
		cmd = 0b00001000
		if inverse: cmd |= 1 << 0
		if enable: cmd |= 1 << 2
		self.spi.writebytes([cmd])

	def _cmd0setY(self, row):
		cmd = 0b01000000
		cmd |= row & 0b00000111
		self.spi.writebytes([cmd])

	def _cmd0setX(self, col):
		cmd = 0b10000000
		cmd |= col & 0b01111111
		self.spi.writebytes([cmd])

	def _cmd1setTC(self, coef = 0):
		# 0: 1mV/K
		# 1: 9mV/K
		# 2: 17mV/K
		# 3: 24mV/K
		cmd = 0b00000100
		cmd |= coef & 0b00000011
		self.spi.writebytes([cmd])

	def _cmd1setBias(self, bias = 3):
		# bias optimum vs. mux:
		# 0	1:100
		# 1	1:80
		# 2	1:65
		# 3	1:48
		# 4	1:40, 1:34
		# 5	1:24
		# 6	1:18, 1:16
		# 7	1:10, 1:9, 1:8
		cmd = 0b00010000
		cmd |= bias & 0b00000111
		self.spi.writebytes([cmd])

	def _cmd1setVOP(self, VOP = 16):
		# Vlcd = 3.06 + VOP*0.06
		# optimum Vlcd: (1 + sqrt(1/mux)) / sqrt(2 * (1 - sqrt(mux)) * Vth
		cmd = 0b10000000
		cmd |= VOP & 0b01111111
		self.spi.writebytes([cmd])

	def reset(self):
		GPIO.output(self.gpio_nrst, GPIO.LOW)
		sleep(1e-6)
		GPIO.output(self.gpio_nrst, GPIO.HIGH)

		self._cmdMode(True)
		self._cmdFunctionSet(cmdSet = 1)
		self._cmd1setTC()
		self._cmd1setVOP(16)
		self._cmd1setBias(3)
		self._cmdMode(False)

		# workaround bug in library only allowing 255 char writes.
		cols = 84 * 8
		while cols > 0:
			wr = 255 if cols > 255 else cols
			cols -= wr
			self.writeCols([0]*wr)

		self._cmdMode(True)
		self._cmdFunctionSet(cmdSet = 0)
		self._cmd0setDisplayControl()
		self._cmd0setX(0)
		self._cmd0setY(0)		
		self._cmdMode(False)

	def setLocation(self, x, y):
		self._cmdMode(True)
		self._cmd0setX(x)
		self._cmd0setY(y)
		self._cmdMode(False)

	def writeCols(self, cols):
		self.spi.writebytes(cols)
