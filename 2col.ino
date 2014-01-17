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

	fb_fill(&fb, COLOR(0,0,0));
	font_draw(&fb, offset, 0, COLOR(16,64,64), "Hello, world");
	font_draw(&fb, offset + 37, 0, COLOR(16,64,64), "Hello, world");
	if (--offset < 37)
		offset = 0;

	ws28_send(&fb);

	delay(1000 / 10);
}
