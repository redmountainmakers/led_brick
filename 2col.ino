#include <gfx.h>

#define COLS	29
#define ROWS	6

color_t fb_buf[COLS*ROWS];
fb_t fb = {
	.width = COLS,
	.height = ROWS,
	.pitch = COLS,
	.buf = fb_buf,
};

static unsigned int counter = 0;
static unsigned int tot_counter = 0;
static unsigned long this_micros;
static int mode = 0;
static color_t c;
static int rmm_len;
static const char rmm[] = "RedMountainMakers";

void setup()
{
	ws28_init();
	rmm_len = font_size(rmm);
}

void nextMode() {
	mode = (mode + 1) % 3;
	counter = 0;
}

void frameDelay(unsigned usec) {
	long delay = (signed long)(this_micros + usec - micros() - 10) /*bad estimate of overhead*/;
	if (delay > 0)
		delayMicroseconds(delay);
}

void doTextDemo() {
	int offset = fb.width - counter/15 - (fb.width - 4);

	fb_fill(&fb, COLOR(0,0,0));

	offset += font_draw(&fb, offset, 0, COLOR(255,0,0), "Red");

	const unsigned char mountain[] = "Mountain";
	for (unsigned char i = 0; mountain[i]; ++i) {
		fb_color_hsv(&c, 40, 255 - 255*i/(sizeof(mountain)-1), 255);
		offset += font_draw_ch(&fb, offset, 0, &c, mountain[i]);
	}

	const unsigned char makers[] = "Makers";
	for (unsigned char i = 0; makers[i]; ++i) {
		fb_color_hsv(&c, (tot_counter - 10*i + 360) % 360, 255, 255);
		offset += font_draw_ch(&fb, offset, 0, &c, makers[i]);
	}

	if (offset <= 0)
		nextMode();

	ws28_send(&fb);
	frameDelay(5000);
}

void doTextDemo2() {
	int offset = counter/15 - rmm_len;

	for (int j = 0; j < COLS; ++j) {
		for (int i = 0; i < ROWS; ++i) {
			fb_color_hsv(&c, (tot_counter + 10*j + 2*i) % 360, 255, 255);
			fb_pixel_set(&fb, j, i, &c);
		}
	}

	font_draw(&fb, offset, 0, COLOR(0,0,0), rmm);
	if (offset > fb.width)
		nextMode();

	ws28_send(&fb);
	frameDelay(5000);
}

void doColorDemo() {
	for (int j = 0; j < COLS; ++j) {
		for (int i = 0; i < ROWS; ++i) {
			fb_color_hsv(&c, (tot_counter + 10*j + 2*i) % 360, 255, 255);
			fb_pixel_set(&fb, j, i, &c);
		}
	}

	if (counter >= 150000/75)
		nextMode();

	ws28_send(&fb);
	frameDelay(7500);
}

void loop()
{
	this_micros = micros();

	switch (mode) {
	case 0: doTextDemo(); break;
	case 1: doTextDemo2(); break;
	case 2: doColorDemo(); break;
	}

	++counter;
	++tot_counter;
}
