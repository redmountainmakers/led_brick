#!/usr/bin/cython

# XXX TODO: Improve compatibility with Adafruit_BBIO.SPI

from libc.stdint cimport uint64_t as u64, uint32_t as u32, uint16_t as u16, uint8_t as u8, uintptr_t
from libc.stddef cimport size_t
from libc.string cimport memset
from posix.ioctl cimport ioctl
from posix.fcntl cimport open, O_RDWR
from posix.unistd cimport close
from cpython.buffer cimport PyObject_GetBuffer, PyBuffer_Release, PyBUF_SIMPLE, PyBUF_WRITABLE
from cpython.cobject cimport PyCObject_FromVoidPtr, PyCObject_AsVoidPtr
from cpython.mem cimport PyMem_Malloc, PyMem_Realloc, PyMem_Free
from numbers import Integral
from copy import copy

cdef extern from "alloca.h" nogil:
	void *alloca(size_t size)

cdef extern from "linux/spi/spidev.h" nogil:
	enum:
		_SPI_CPHA "SPI_CPHA"
		_SPI_CPOL "SPI_CPOL"

		_SPI_MODE_0 "SPI_MODE_0"
		_SPI_MODE_1 "SPI_MODE_1"
		_SPI_MODE_2 "SPI_MODE_2"
		_SPI_MODE_3 "SPI_MODE_3"

		_SPI_CS_HIGH "SPI_CS_HIGH"
		_SPI_LSB_FIRST "SPI_LSB_FIRST"
		_SPI_3WIRE "SPI_3WIRE"
		_SPI_LOOP "SPI_LOOP"
		_SPI_NO_CS "SPI_NO_CS"
		_SPI_READY "SPI_READY"

	int SPI_IOC_MESSAGE(int count)
	enum:
		SPI_IOC_RD_MODE
		SPI_IOC_WR_MODE
		SPI_IOC_RD_LSB_FIRST
		SPI_IOC_WR_LSB_FIRST
		SPI_IOC_RD_BITS_PER_WORD
		SPI_IOC_WR_BITS_PER_WORD
		SPI_IOC_RD_MAX_SPEED_HZ
		SPI_IOC_WR_MAX_SPEED_HZ

	struct spi_ioc_transfer:
		u64 tx_buf, rx_buf
		u32 len
		u32 speed_hz
		u16 delay_usecs
		u8 bits_per_word
		u8 cs_change
		u32 pad

SPI_CPOL = _SPI_CPOL
SPI_CPHA = _SPI_CPHA

SPI_MODE_0 = _SPI_MODE_0
SPI_MODE_1 = _SPI_MODE_1
SPI_MODE_2 = _SPI_MODE_2
SPI_MODE_3 = _SPI_MODE_3

SPI_CS_HIGH = _SPI_CS_HIGH
SPI_LSB_FIRST = _SPI_LSB_FIRST
SPI_3WIRE = _SPI_3WIRE
SPI_LOOP = _SPI_LOOP
SPI_NO_CS = _SPI_NO_CS
SPI_READY = _SPI_READY

# omap2-mcspi DMA workaround
cdef size_t DMA_MIN_BYTES = 160

cdef class SPI:
	cdef int fd
	cdef u8 _mode
	cdef int _saved_sched, _saved_prio
	cdef spi_ioc_transfer def_transfer
	cdef object _buffers

	def __cinit__(self):
		self.fd = -1
		self._mode = 0

	def __dealloc__(self):
		self.close()

	def __init__(self, file = "/dev/spidev1.0", mode = _SPI_MODE_0, speed_hz = 25000000, bpw = 8, delay_us = 0, cs_change = False):
		self._buffers = []

		if file is not None:
			self.open(file)

			if mode is not None: self.mode = mode
			if speed_hz is not None: self.speed_hz = speed_hz
			if bpw is not None: self.bpw = bpw
			if delay_us is not None: self.delay_us = delay_us
			if cs_change is not None: self.cs_change = cs_change

	def open(self, file):
		self.fd = open(file, O_RDWR)
		if self.fd < 0:
			raise IOError(-self.fd, "Unable to open %s" % (file))

		memset(&self.def_transfer, 0, sizeof(self.def_transfer));
		self._mode = 0

		ioctl(self.fd, SPI_IOC_RD_MODE, &self._mode)
		ioctl(self.fd, SPI_IOC_RD_BITS_PER_WORD, &self.def_transfer.bits_per_word)
		ioctl(self.fd, SPI_IOC_RD_MAX_SPEED_HZ, &self.def_transfer.speed_hz)

	cdef void close(self) nogil:
		if self.fd >= 0:
			close(self.fd)
			self.fd = -1

	def write(self, data):
		self.transact(txdata = data, rxdata = None)

	def exchange(self, data, out = None):
		self.transact(txdata = data, rxdata = data if out is None else out)

	def read(self, buffersize):
		out = bytearray(int(buffersize))
		self.transact(txdata = int(buffersize), rxdata = out)
		return out

	def ignore(self, buffersize):
		self.transact(txdata = int(buffersize), rxdata = None)

	cdef int _transact(self, spi_ioc_transfer *msg, int msgs) nogil:
		cdef int ret
		ret = ioctl(self.fd, SPI_IOC_MESSAGE(msgs), <void*>msg)
		return ret

	cdef u64 _pybuf_get(self, object data, bint writable, int itemsize) except <u64>-1:
		cdef Py_buffer *buf
		cdef int flags = PyBUF_SIMPLE

		if data is None:
			return <u64>0

		if writable:
			flags |= PyBUF_WRITABLE

		buf = <Py_buffer*>PyMem_Malloc(sizeof(Py_buffer))

		PyObject_GetBuffer(data, buf, flags)
		if itemsize != buf.itemsize:
			PyBuffer_Release(buf)
			PyMem_Free(<void*>buf)
			raise IOError("itemsize mismatch")
		self._buffers.append(PyCObject_FromVoidPtr(<void*>buf, PyMem_Free))
		return <u64><uintptr_t>buf.buf

	def _pybuf_putall(self):
		cdef Py_buffer *buf
		for buffer in self._buffers:
			buf = <Py_buffer*>PyCObject_AsVoidPtr(buffer)
			PyBuffer_Release(buf)
		self._buffers = []

	def transact(self, transactions = None, txdata = None, rxdata = None, speed_hz = None, bpw = None, delay_us = None, cs_change = None):
		cdef size_t tlen
		cdef int count
		cdef spi_ioc_transfer *x
		cdef int i, ret

		if transactions is None:
			tr = {
				'tx': txdata,
				'rx': rxdata
			}
			if speed_hz is not None: tr['speed_hz'] = speed_hz
			if bpw is not None: tr['bpw'] = bpw
			if delay_us is not None: tr['delay_us'] = delay_us
			if cs_change is not None: tr['cs_change'] = cs_change
			transactions = [ tr ]

		# Copy needed for omap2-mcspi workaround, which inserts into transactions.
		for tr in copy(transactions):
			bpw = tr['bpw'] if 'bpw' in tr else self.def_transfer.bits_per_word
			if bpw == 0: bpw = 8
			itemsize = (bpw + 7) / 8
			tr['bpw'] = bpw

			trtx = tr['tx'] if 'tx' in tr else None
			trrx = tr['rx'] if 'rx' in tr else None

			if isinstance(trtx, Integral):
				tlen = trtx
				trtx = None
			elif trtx is not None:
				tlen = len(trtx)
			else:
				tlen = len(trrx)

			tlen *= itemsize

			tr['len'] = tlen

			tr['tx_buf'] = self._pybuf_get(trtx, trrx is trtx and trtx is not None, itemsize)
			if trrx is not trtx:
				tr['rx_buf'] = self._pybuf_get(trrx, True, itemsize)
			else:
				tr['rx_buf'] = tr['tx_buf']

			tr['tx'] = None
			tr['rx'] = None

			# omap2-mcspi dma workaround - DMA transfers hang or cause
			# various timeouts, so we split the buffers in to sizes small
			# enough that the driver will not use DMA for them.
			while tlen >= DMA_MIN_BYTES:
				clamp_tlen = ((DMA_MIN_BYTES - 1) & ~(itemsize-1))
				new_tlen = tlen - clamp_tlen
				tlen = clamp_tlen

				new_tr = copy(tr)
				if tr['tx_buf']: new_tr['tx_buf'] = tr['tx_buf'] + tlen
				if tr['rx_buf']: new_tr['rx_buf'] = tr['rx_buf'] + tlen
				new_tr['len'] = new_tlen
				tr['len'] = tlen
				transactions.insert(transactions.index(tr) + 1, new_tr)
				tr = new_tr
				tlen = tr['len']

		count = len(transactions)
		try:
			x = <spi_ioc_transfer *>alloca(sizeof(spi_ioc_transfer) * count)
			for i in range(0, count):
				tr = transactions[i]

				x[i] = self.def_transfer
				if 'speed_hz' in tr: x[i].speed_hz = tr['speed_hz']
				x[i].bits_per_word = tr['bpw']
				if 'delay_us' in tr: x[i].delay_usecs = tr['delay_us']
				if 'cs_change' in tr: x[i].cs_change = tr['cs_change']

				x[i].tx_buf = tr['tx_buf']
				x[i].rx_buf = tr['rx_buf']
				x[i].len = tr['len']

			ret = self._transact(&x[0], count)
			if ret < 0:
				raise IOError(-ret, "SPI transaction error")

		finally:
			self._pybuf_putall()

	property mode:
		def __get__(self):
			return self._mode

		def __set__(self, value):
			cdef int ret
			cdef u8 mode = value
			ret = ioctl(self.fd, SPI_IOC_WR_MODE, &mode)
			if ret < 0:
				raise IOError(-ret, "Couldn't set SPI mode")
			self._mode = mode

	property bpw:
		def __get__(self):
			return self.def_transfer.bits_per_word
		def __set__(self, value):
			cdef u8 bpw = value
			ioctl(self.fd, SPI_IOC_WR_BITS_PER_WORD, &bpw)
			self.def_transfer.bits_per_word = bpw

	property speed_hz:
		def __get__(self):
			return self.def_transfer.speed_hz
		def __set__(self, value):
			cdef u32 speed_hz = value
			ioctl(self.fd, SPI_IOC_WR_MAX_SPEED_HZ, &speed_hz)
			self.def_transfer.speed_hz = speed_hz

	property delay_us:
		def __get__(self):
			return self.def_transfer.delay_usecs
		def __set__(self, value):
			self.def_transfer.delay_usecs = value

	property cs_change:
		def __get__(self):
			return self.def_transfer.cs_change
		def __set__(self, value):
			self.def_transfer.cs_change = value

	cdef bint _mode_get_bit(self, u8 mask) nogil:
		return (self._mode & mask) != 0

	cdef bint _mode_get_bit_explicit(self, u8 mask) except -1:
		cdef int ret
		cdef u8 mode
		ret = ioctl(self.fd, SPI_IOC_RD_MODE, &mode)
		if ret < 0:
			raise IOError(-ret, "Couldn't read SPI mode")
		# may as well update it.
		self._mode = mode
		return (mode & mask) != 0

	cdef bint _mode_set_bit(self, u8 mask, bint value) except -1:
		cdef int ret
		cdef u8 mode = self._mode
		if value: mode |= mask
		else: mode &= ~mask
		self.mode = mode
		return 0

	property cpha:
		def __get__(self): return self._mode_get_bit(_SPI_CPHA)
		def __set__(self, value): self._mode_set_bit(_SPI_CPHA, value)

	property cpol:
		def __get__(self): return self._mode_get_bit(_SPI_CPOL)
		def __set__(self, value): self._mode_set_bit(_SPI_CPOL, value)

	property lsbfirst:
		def __get__(self): return self._mode_get_bit(_SPI_LSB_FIRST)
		def __set__(self, value): self._mode_set_bit(_SPI_LSB_FIRST, value)

	property cshigh:
		def __get__(self): return self._mode_get_bit(_SPI_CS_HIGH)
		def __set__(self, value): self._mode_set_bit(_SPI_CS_HIGH, value)

	property threewire:
		def __get__(self): return self._mode_get_bit(_SPI_3WIRE)
		def __set__(self, value): self._mode_set_bit(_SPI_3WIRE, value)

	property loop:
		def __get__(self): return self._mode_get_bit(_SPI_LOOP)
		def __set__(self, value): self._mode_set_bit(_SPI_LOOP, value)

	property no_cs:
		def __get__(self): return self._mode_get_bit(_SPI_NO_CS)
		def __set__(self, value): self._mode_set_bit(_SPI_NO_CS, value)

	property ready:
		def __get__(self): return self._mode_get_bit_explicit(_SPI_READY)
