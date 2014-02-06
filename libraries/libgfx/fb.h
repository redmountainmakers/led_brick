#ifndef FB_h_a0f8b242_77c9_11e3_a792_0013e831a5cf
#define FB_h_a0f8b242_77c9_11e3_a792_0013e831a5cf
/**
 * SECTION:fb
 * @short_description: Basic framebuffer/color support
 *
 * Contains low-level functions for framebuffer and color/pixel support.
 * <warning>None of these functions do bounds checking - that is the
 * responsibility of higher level code.</warning>
 */

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>
#include <string.h> /* memcpy */


/**
 * color_t:
 *
 * Type representing a color or single pixel.
 */
typedef uint16_t color_t;

/**
 * FB_EPP:
 *
 * Number of elements per pixel in #fb_t.buf.
 */
#define FB_EPP		1

/**
 * fb_t:
 * @width: Width of the framebuffer.
 * @height: Height of the framebuffer.
 * @pitch: Pitch of the framebuffer (<emphasis>elements</emphasis> to next row).
 * @buf: (array): Framebuffer pixels; Must have at least <code>#fb_t.height * #fb_t.pitch</code> elements.
 *
 * A basic framebuffer object with @width columns and @height rows of pixels.
 */
typedef struct fb_s {
	int width, height;
	int pitch;
	color_t *buf;
} fb_t;

/**
 * COLOR:
 * @r: (in) (type uint8_t): Red value (0 to 255)
 * @g: (in) (type uint8_t): Red value (0 to 255)
 * @b: (in) (type uint8_t): Red value (0 to 255)
 *
 * Converts R,G,B values in to a #color_t
 *
 * Returns: <code>const</code> pointer to the #color_t
 */
#define COLOR(r,g,b) \
	(const color_t[1]){ \
		((((unsigned int)r)>>3) & 0x001f) | \
		((((unsigned int)g)<<3) & 0x07e0) | \
		((((unsigned int)b)<<8) & 0xf800) }

/**
 * FB_DEF:
 * @name: (type fb_t): Name of the #fb_t variable to declare and define.
 * @w: (type int) (in): Width of the framebuffer to allocate.
 * @h: (type int) (in): Height of the framebuffer to allocate.
 *
 * Staticly allocate and initialize a #fb_t and its buffer.
 */
#define FB_DEF(name,w,h) \
	color_array_t name ## _buf[(w)*(h)]; \
	fb_t name = { \
		.width = (w), .height = (h), \
		.pitch = (w)*(h), \
		.buf = name ## _buf, \
	};

/**
 * fb_init:
 * @fb_out: (out): The framebuffer to initialize.
 * @buf: (in): The allocated memory.  Must be at least <code>@h * @pitch</code> elements.
 * @w: (in): Width of the framebuffer.
 * @h: (in): Height of the framebuffer.
 * @pitch: (in): Number of <emphasis>elements</emphasis> to get from one row to the next.
 *
 * Initialize a #fb_t with pre-allocated buffer.
 *
 * See also: FB_DEF(), fb_sub(), fb_pixel_set(), fb_pixel()
 */
void fb_init(fb_t *fb_out, color_t *buf, int w, int h, int pitch);

/**
 * fb_sub:
 * @fb_out: (out): The framebuffer to initialize.
 * @fb_in: (in): The already-initialized framebuffer.
 * @x0: (in): Left location of the rectangle.
 * @y0: (in): Top location of the rectangle.
 * @w: (in): Width of the rectangle.
 * @h: (in): Height of the rectangle.
 *
 * Initialize a #fb_t as rectangular subset of an existing #fb_t.
 *
 * <note>The data is not copied; changes to @fb_in will appear in @fb_out and vice versa.</note>
 */
void fb_sub(fb_t *fb_out, fb_t *fb_in, int x0, int y0, int w, int h);

/**
 * fb_offset:
 * @fb: (in): The #fb_t
 * @x: (in): X location in @fb
 * @y: (in): Y location in @fb
 *
 * Calculates the element index of a location in a #fb_t.
 *
 * Returns: The index, such that <code>@fb->buf[index]</code> is the pixel at @x,@y
 *
 * See also: fb_pixel(), fb_color_set()
 */
static inline int
fb_offset(
	const fb_t *fb,
	int x,
	int y
)
{
	return fb->pitch*y + x*FB_EPP;
}

/**
 * fb_color_set:
 * @dst: (out): Destination #color_t.
 * @src: (in): Source #color_t.
 *
 * Set #color_t @dst to the color in @src.
 *
 * See also: fb_pixel_set(), fb_pixel()
 */
static inline void
fb_color_set(
	color_t *dst,
	const color_t *src
)
{
	memcpy(dst, src, sizeof(color_t)*FB_EPP);
}

/**
 * fb_pixel:
 * @fb: (in): Framebuffer containing the pixel.
 * @x: (in): X location in @fb.
 * @y: (in): Y location in @fb.
 *
 * Calcluate pointer to a pixel in a #fb_t.
 *
 * Returns: A pointer to the requested pixel in @fb.
 *
 * See also: fb_color_set(), fb_pixel_set(), fb_offset()
 */
static inline color_t *
fb_pixel(
	fb_t *fb,
	int x,
	int y
)
{
	return &fb->buf[fb_offset(fb, x, y)];
}

/**
 * fb_pixel_set:
 * @fb: (in): Framebuffer to set the pixel in.
 * @x: (in): X location in @fb.
 * @y: (in): Y location in @fb.
 * @src: (in): #color_t to set the pixel at @x,@y in @fb to.
 *
 * Set a pixel in a #fb_t to a #color_t.
 *
 * See also: COLOR(), fb_color_hsv(), fb_pixel()
 */
static inline void
fb_pixel_set(
	fb_t *fb,
	int x,
	int y,
	const color_t *src
)
{
	memcpy(fb_pixel(fb, x, y), src, sizeof(color_t)*FB_EPP);
}

/**
 * fb_fill:
 * @fb_out: (in): The #fb_t to fill.
 * @color: (in): The #color_t to fill @fb_out with.
 *
 * Fill an entire #fb_t with one color.
 */
void fb_fill(fb_t *fb_out, const color_t *color);

/**
 * fb_color_hsv:
 * @dst: (out): #color_t to store the result in.
 * @h: (in): Hue of @dst in degrees (0 to 359).
 * @s: (in): Saturation of @dst (0 to 255).
 * @v: (in): Value of @dst (0 to 255).
 *
 * Create a #color_t based on Hue, Saturation, and Value.
 *
 * See also: COLOR(), fb_pixel_set(), fb_color_set()
 */
void fb_color_hsv(color_t *dst, unsigned int h, unsigned int s, unsigned int v);

#ifdef __cplusplus
};
#endif

#endif
