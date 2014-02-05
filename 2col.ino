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

void setup()
{
	ws28_init();
}

void loop()
{
	static int offset = 0;
	static int hue = 0;
	static color_t c;

#if 0
	fb_fill(&fb, COLOR(0,0,0));
	font_draw(&fb, offset, 0, &c, "Hello, world");
	font_draw(&fb, offset + 38, 0, &c, "Hello, world");
	if (--offset < -38)
		offset = 0;
#else
#if 0
	fb_fill(&fb, &c);
#else
	fb_fill(&fb, COLOR(0,0,0));
	for (int j = 0; j < COLS; ++j) {
		for (int i = 0; i < ROWS; ++i) {
			fb_color_hsv(&c, (hue + 10*j) % 360, 255, 255);
			fb_pixel_set(&fb, j, i, &c);
		}
	}
#endif
#endif

	hue = (hue + 1) % 360;

	ws28_send(&fb);

	delay(5);
}
