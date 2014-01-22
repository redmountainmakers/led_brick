#ifndef FB_h_a0f8b242_77c9_11e3_a792_0013e831a5cf
#define FB_h_a0f8b242_77c9_11e3_a792_0013e831a5cf

#include <stdint.h>
#include <string.h> /* memcpy */

typedef uint16_t color_t;

#define FB_EPP		1	/* Elements per pixel */

typedef struct fb_s fb_t;
struct fb_s {
	int width, height;
	int pitch; /* in elements, not pixels */
	color_t *buf;
};

#define COLOR(r,g,b) \
	(const color_t[1]){ \
		(((r)>>3) & 0x001f) | \
		(((g)<<3) & 0x07e0) | \
		(((b)<<8) & 0xf800) }

static inline int fb_offset(const fb_t *fb, int x, int y)
{
	return fb->pitch*y + x*FB_EPP;
}

static inline void fb_color_set(color_t *dst, const color_t *src)
{
	memcpy(dst, src, sizeof(color_t)*FB_EPP);
}

static inline color_t *fb_pixel(fb_t *fb, int x, int y)
{
	return &fb->buf[fb_offset(fb, x, y)];
}

static inline void fb_pixel_set(fb_t *fb, int x, int y, const color_t *src)
{
	memcpy(fb_pixel(fb, x, y), src, sizeof(color_t)*FB_EPP);
}

/* staticly allocate and initialize a framebuffer */
#define FB_DEF(name,w,h) \
	color_array_t name ## _buf[(w)*(h)]; \
	fb_t name = { \
		.width = (w), .height = (h), \
		.pitch = (w)*(h), \
		.buf = name ## _buf, \
	};

#ifdef __cplusplus
extern "C" {
#endif

/* initialize a framebuffer w/ pointer to existing memory */
void fb_init(fb_t *fb_out, color_t *buf, int w, int h, int pitch);

/* initialize a framebuffer that is a subset of an existing framebuffer */
void fb_sub(fb_t *fb_out, fb_t *fb_in, int x0, int y0, int w, int h);

void fb_fill(fb_t *fb_out, const color_t *color);

void fb_color_hsv(color_t *dst, int h, int s, int v);

#ifdef __cplusplus
};
#endif

#endif
