#include <stdint.h>
#include <stdio.h>

#include "fb.h"
#include "font.h"
#include "font_data.h"

/* Draw a character using the offset+bitmap encoded font data.
 * The font is encoded as a set of offsets (font.pos) to the first
 * column of each letter in a bitmap.  The bitmap is stored by column,
 * and characters are packed in order with no blank columns between them.
 *
 * font.pos[256] is where the start of a hypothetical character
 * following '\xff' would be, but there is no data there.
 *
 * ( font.data[font.pos[ch + col]] << row ) is the bit associated with
 * each row/column, with 1 being set and 0 being not set.  font.data may
 * be any unsigned integer type up to uint32_t to account for the
 * number of rows present in the font (32 maximum).
 *
 * Some skipping of initial columns and/or rows is performed when the
 * starting location is out of bounds, and the function returns early
 * if the top location is out of bounds, or the left location is out
 * of bounds.  The early return does not affect the return value.
 */
int font_draw_ch(fb_t *fb, int sx, int sy, const color_t *color, unsigned char ch)
{
	int c0, c1, len, skip_y;

	c0 = font.pos[ch];
	c1 = font.pos[ch + 1];
	len = c1 - c0;

	skip_y = 0;

	if (sx < 0) {
		int skip_x = -sx;
		if (skip_x >= len)
			return len + 1;
		sx = 0;
		c0 += skip_x;
	}

	if (sy < 0) {
		skip_y = -sy;
		if (skip_y >= 8*FONT_COL_BYTES)
			return len + 1;
		sy = 0;
	}

	for (; c0 < c1 && sx < fb->width; ++c0, ++sx) {
		int bit = skip_y % 8;
		int r = skip_y / 8;
		int y = sy + r*8;

		for (; r < FONT_COL_BYTES; ++r) {
			unsigned bits = font.data[c0] >> bit;

			while (bits && (y + bit) < fb->height) {
				if (bits & 1)
					fb_pixel_set(fb, sx, y + bit, color);
				bits >>= 1;
				++bit;
			}

			y += 8;
			bit = 0;
		}
	}

	return len + 1;
}

int font_draw(fb_t *fb, int sx, int sy, const color_t *color, const char *str)
{
	int len = 0;
	for (; *str; ++str)
		len += font_draw_ch(fb, sx + len, sy, color, *str & 0xff);
	return len;
}

int font_size_ch(unsigned char ch)
{
	return font.pos[ch+1] - font.pos[ch];
}

int font_size(const char *str)
{
	int len = 0;
	for (; *str; ++str)
		len += font_size_ch(*str & 0xff) + 1;
	return len;
}
