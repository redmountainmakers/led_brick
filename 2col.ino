#include <gfx.h>

#define COLS	2
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

	fb_color_hsv(&c, hue, 255, 64);

#if 1
	fb_fill(&fb, COLOR(0,0,0));
	font_draw(&fb, offset, 0, &c, "Hello, world");
	font_draw(&fb, offset + 38, 0, &c, "Hello, world");
	if (--offset < -38)
		offset = 0;
#else
	fb_fill(&fb, &c);
#endif

	hue = (hue + 1) % 360;

	ws28_send(&fb);

	delay(100);
}
