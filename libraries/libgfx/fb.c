#include <assert.h>

#include "fb.h"

/* initialize a framebuffer w/ pointer to existing memory */
void fb_init(fb_t *fb_out, color_t *buf, int w, int h, int pitch)
{
	fb_out->width = w;
	fb_out->height = h;
	fb_out->pitch = pitch;
	fb_out->buf = buf;
}

/* initialize a framebuffer that is a subset of an existing framebuffer */
void fb_sub(fb_t *fb_out, fb_t *fb_in, int x0, int y0, int w, int h)
{
	assert(x0 >= 0 && y0 >= 0 &&
		(x0 + w) <= fb_in->width && (y0 + h) <= fb_in->height);

	fb_out->width = w;
	fb_out->height = h;
	fb_out->pitch = fb_in->pitch;
	fb_out->buf = &fb_in->buf[y0*fb_in->pitch + x0*FB_EPP];
}

void fb_fill(fb_t *fb_out, const color_t *color)
{
	for (int y = 0; y < fb_out->height; ++y) {
		color_t *row = &fb_out->buf[y*fb_out->pitch];
		for (int x = 0; x < fb_out->width; ++x)
			fb_color_set(&row[x*FB_EPP], color);
	}
}

void fb_color_hsv(color_t *dst, unsigned int h, unsigned int s, unsigned int v)
{
	unsigned int c, x, hm;
	uint8_t r, g, b;

	c = s*v/255;
	hm = h % 120;
	if (hm >= 60) hm = 120 - hm;

	h /= 60;
	x = hm*c/60;

	switch (h) {
	case 0: r = c; g = x; b = 0; break;
	case 1: r = x; g = c; b = 0; break;
	case 2: r = 0; g = c; b = x; break;
	case 3: r = 0; g = x; b = c; break;
	case 4: r = x; g = 0; b = c; break;
	case 5: r = c; g = 0; b = x; break;
	default: r = 0; g = 0; b = 0; break;
	}

	hm = v - c;
	r += hm;
	g += hm;
	b += hm;
	fb_color_set(dst, COLOR(r,g,b));
}
