#include <stdint.h>

#include <SPI.h>

#include "fb.h"
#include "ws28.h"

#define SS_PIN	10

static unsigned long fb_last_micros = 0;

/* initialize SPI for ws28 operations */
void ws28_init(void)
{
	SPI.begin();
	SPI.setClockDivider(SPI_CLOCK_DIV16);
	SPI.setBitOrder(MSBFIRST);
	SPI.setDataMode(SPI_MODE0);
#ifdef SS_PIN
	pinMode(SS_PIN, OUTPUT);
#endif
}

/* Send a single color to SPI-connected ws28xx */
void ws28_send_color(const color_t *src)
{
	uint8_t rgb[3];

	rgb[0] = (*src & 0x001f) << 3;
	rgb[0] |= rgb[0] >> 5;

	rgb[1] = (*src & 0x07e0) >> 3;
	rgb[1] |= rgb[1] >> 6;

	rgb[2] = (*src & 0xf800) >> 8;
	rgb[2] |= rgb[2] >> 5;

	SPI.transfer(rgb[0]);
	SPI.transfer(rgb[1]);
	SPI.transfer(rgb[2]);
}

/* Send the framebuffer to SPI-connected ws28xx */
void ws28_send(fb_t *fb)
{
	unsigned long time_diff = micros() - fb_last_micros;
	if (time_diff < 600)
		delayMicroseconds(600 - time_diff);

	for (int x = 0; x < fb->width; ++x) {
		for (int y = 0; y < fb->height; ++y)
			ws28_send_color(fb_pixel(fb, x, y));
	}

	fb_last_micros = micros();
}
