#include "ch.h"
#include "hal.h"
#include "usbcfg.h"
#include <gfx.h>

#define usb_lld_connect_bus(usbp)
#define usb_lld_disconnect_bus(usbp)

SerialUSBDriver SDU1;

enum { LED_NOCONN, LED_CONN };
static unsigned int led_on = 0, led_off = 0;
static unsigned int led_onbase[] = { 0, 0 };
static const systime_t led_ms[] = { MS2ST(500), MS2ST(250) };
static const unsigned int led_bit[] = { GPIOE_LED10_RED, GPIOE_LED7_GREEN };

static void led_set(int num, int on, int time)
{
	unsigned int port_bit = PAL_PORT_BIT(led_bit[num]);

	if (on) {
		if (!(led_on & port_bit)) {
			led_onbase[num] = time;
			led_on |= port_bit;
		}
		led_off &= ~port_bit;
		if (((led_onbase[num] - time) / led_ms[num]) & 1) {
			led_off |= port_bit;
		}
	} else {
		led_on &= ~port_bit;
		led_off |= port_bit;
	}
}

static WORKING_AREA(blink_thread_wa, 128);
static __attribute__((noreturn)) msg_t blink_thread(void *arg __attribute__((unused)))
{
	while (TRUE) {
		unsigned int this_time = chTimeNow();

		led_set(LED_NOCONN, SDU1.config->usbp->state != USB_ACTIVE, this_time);
		led_set(LED_CONN, SDU1.config->usbp->state == USB_ACTIVE, this_time);

		palSetPort(GPIOE, led_on & ~led_off);
		palClearPort(GPIOE, led_off);
		
		chThdSleepMilliseconds(10);
	}
}

#define COLS	29
#define ROWS	6
static color_t fb_data[COLS*ROWS];
static fb_t fb = {
	.width = COLS, .height = ROWS,
	.pitch = COLS*FB_EPP,
	.buf = fb_data,
};

static int hue = 0;
static int offset = 0;

int main(void)
{
	static int button_state = 0;

	halInit();
	chSysInit();

	palSetPad(GPIOE, GPIOE_LED4_BLUE);

#if 0
	/* USB setup */
	palClearPort(GPIOA, PAL_PORT_BIT(GPIOA_USB_DM) | PAL_PORT_BIT(GPIOA_USB_DP));
	palSetGroupMode(GPIOA, PAL_PORT_BIT(GPIOA_USB_DM) | PAL_PORT_BIT(GPIOA_USB_DP), 0, PAL_MODE_OUTPUT_OPENDRAIN);
	chThdSleepMilliseconds(100);

	serusb_init();
	sduObjectInit(&SDU1);
	sduStart(&SDU1, &serusbcfg);

	palSetGroupMode(GPIOA,
		PAL_PORT_BIT(GPIOA_USB_DM) | PAL_PORT_BIT(GPIOA_USB_DP), 0,
		PAL_MODE_ALTERNATE(14) | PAL_STM32_OSPEED_HIGHEST);
#endif

	palSetPad(GPIOE, GPIOE_LED3_RED);

	/* ws28xx */
	ws28_init();

	/* final stage */
	palClearPort(GPIOE,
		PAL_PORT_BIT(GPIOE_LED4_BLUE) |
		PAL_PORT_BIT(GPIOE_LED3_RED) |
		PAL_PORT_BIT(GPIOE_LED5_ORANGE) |
		PAL_PORT_BIT(GPIOE_LED7_GREEN));

	/* blink thread */
	chThdCreateStatic(blink_thread_wa, sizeof(blink_thread_wa), NORMALPRIO, blink_thread, NULL);

	palSetPad(GPIOE, GPIOE_LED6_GREEN);

	fb_fill(&fb, COLOR(0,0,0));
	ws28_send(&fb);

	/* data pump */
	while (TRUE) {
		int new_state = palReadPad(GPIOA, GPIOA_BUTTON);
		if (new_state != button_state) {
			button_state = new_state;
			if (new_state) {
				palSetPad(GPIOE, GPIOE_LED8_ORANGE);
			} else {
				palClearPad(GPIOE, GPIOE_LED8_ORANGE);
			}
		}

#if 1
		for (int x = 0; x < COLS; ++x) {
			for (int y = 0; y < ROWS; ++y) {
				fb_color_hsv(fb_pixel(&fb,x,y), (hue + y*90) % 360, 255, 64);
			}
		}
#else
		fb_fill(&fb, COLOR(0, 0, 0));
#endif

#if 0
		font_draw(&fb, offset, 0, COLOR(255, 255, 255), "Hello, world.");
		font_draw(&fb, offset + 39, 0, COLOR(255, 255, 255), "Hello, world.");
		offset = (offset - 1) % 39;
#endif

		hue = (hue + 1) % 360;

		ws28_send(&fb);

		chThdSleepMilliseconds(10);
	}
}
