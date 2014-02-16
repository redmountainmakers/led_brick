#include <stdint.h>

#include "ch.h"
#include "hal.h"

#include "fb.h"
#include "ws28.h"

static const SPIConfig spicfg = {
	NULL,
	GPIOB,
	12,
	SPI_CR1_BR_2 | SPI_CR1_BR_0, /* 1.1125MHz */
	SPI_CR2_DS_2 | SPI_CR2_DS_1 | SPI_CR2_DS_0
};

static systime_t fb_last_draw = 0;

/* initialize SPI for ws28 operations */
void ws28_init(void)
{
	palSetPadMode(GPIOB, 12, PAL_MODE_OUTPUT_PUSHPULL | PAL_STM32_OSPEED_HIGHEST);
	palSetPadMode(GPIOB, 13, PAL_MODE_ALTERNATE(5) | PAL_STM32_OSPEED_HIGHEST);
	palSetPadMode(GPIOB, 14, PAL_MODE_ALTERNATE(5) | PAL_STM32_OSPEED_HIGHEST);
	palSetPadMode(GPIOB, 15, PAL_MODE_ALTERNATE(5) | PAL_STM32_OSPEED_HIGHEST);
	palClearPad(GPIOB, 13);
	palClearPad(GPIOB, 14);
	palClearPad(GPIOB, 15);
	palSetPad(GPIOB, 12);
/*	spiStart(&SPID2, &spicfg);
	spiSelect(&SPID2);*/
}

static uint8_t spi_buf[29*6*sizeof(color_t)*FB_EPP];
static uint8_t *spi_p = spi_buf;

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

	memcpy(spi_p, rgb, 3);
	spi_p += 3;
}

/* Send the framebuffer to SPI-connected ws28xx */
#define ST2US(x)	\
	(uint32_t)((systime_t)(x) * 1000000UL / (systime_t)CH_FREQUENCY)
void ws28_send(fb_t *fb)
{
	systime_t time_diff = ST2US(chTimeNow() - fb_last_draw);
	if (time_diff < US2ST(600))
		chThdSleepMicroseconds(600 - time_diff);

	for (int i = 0; i < fb->width; ++i) {
		for (int j = 0; j < fb->height; ++j)
			ws28_send_color(&fb->buf[j*fb->pitch + i*FB_EPP]);
	}

	spiStart(&SPID2, &spicfg);
	spiSelect(&SPID2);
	spiSend(&SPID2, spi_p - spi_buf, spi_buf);
	spiUnselect(&SPID2);
	spiStop(&SPID2);
	spi_p = spi_buf;

	fb_last_draw = chTimeNow();
}
