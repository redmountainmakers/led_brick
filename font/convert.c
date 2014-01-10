/*
	convert.c - convert a gimp_image .c font to a more compact format.
	Copyright (C) 2014  Red Mountain Makers
	
	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.
	
	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.
	
	You should have received a copy of the GNU General Public License
	along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#include <stdio.h>
#include <stdint.h>
#include <string.h>

#include "6by6.c"

#define bpp (gimp_image.bytes_per_pixel)
#define pitch (gimp_image.width * bpp)
#define cell_w (gimp_image.width / 16)
#define cell_h (gimp_image.height / 16)
#define char_w (cell_w - 1)
#define char_h (cell_h - 1)
#define col_bytes ((char_h + 7) / 8)

static inline uint8_t *put_bytes(uint8_t *p, uint32_t val, int bytes)
{
	while (bytes--) {
		*p++ = val & 0xff;
		val >>= 8;
	}
	return p;
}

/* no need to be clever.. */
static int bytes_for_value(uint32_t value)
{
	int bytes = 1;
	value += 7;
	value /= 256;
	while (value) {
		++bytes;
		value /= 256;
	}
	return bytes;
}

static void print_ints(const uint32_t *buf, int len, const char *prefix, int max_cols)
{
	int i;
	int ccol = 0;
	char dec[16];

	max_cols -= 2; /* dquotes */

	for (i = 0; i < len; ++i) {
		int len;

		snprintf(dec, sizeof(dec), "%d,", buf[i]);

		len = strlen(dec);
		if ((ccol + len) >= max_cols) {
			printf("\n");
			ccol = 0;
		}

		if (ccol == 0)
			printf("%s", prefix);

		printf("%s", dec);
		ccol += len;
	}

	if (ccol)
		printf("\n");
}

static void print_bytes(const uint8_t *buf, int len, const char *prefix, int max_cols)
{
	int i;
	int ccol = 0, Qs = 0;

	max_cols -= 2; /* dquotes */

	for (i = 0; i < len; ++i) {
		const char *fmt = NULL;
		char octal[6];
		int ch_len;

		if (buf[i] != '?') Qs = 0;
		else ++Qs;

		switch (buf[i]) {
		case '\a': fmt = "\\a"; break;
		case '\b': fmt = "\\b"; break;
		case '\t': fmt = "\\t"; break;
		case '\n': fmt = "\\n"; break;
		case '\v': fmt = "\\v"; break;
		case '\f': fmt = "\\f"; break;
		case '\r': fmt = "\\r"; break;
		case '"': fmt = "\\\""; break;

		/* escape every other ? in a sequence of ?'s to avoid trigraphs */
		/* note: if this causes a wrap, odd ?'s are escaped instead of even. */
		/*       this is safe; it has no effect on the data. */
		case '?': fmt = (Qs % 2) ? "?" : "\\?"; break;

		case '\\': fmt = "\\\\"; break;

		default:
			/* other non-printable, handled specially */
			if (buf[i] < ' ') {
				int olen = (buf[i] <= 7) ? 2 : 3; /* characters */
				if (i < (len - 1) && ccol < (max_cols - olen - 1) && buf[i+1] >= '0' && buf[i+1] <= '7') {
					/* doesn't wrap or end, and is followed by an octal digit, print all 3 digits. */
					snprintf(octal, sizeof(octal), "\\%03o", (int)buf[i]);
				} else {
					/* we can print the short version */
					snprintf(octal, sizeof(octal), "\\%o", (int)buf[i]);
				}
			} else if (buf[i] >= 127) {
				/* characters > 64 aka '@' are all three digits. */
				snprintf(octal, sizeof(octal), "\\%03o", (int)buf[i]);
			} else {
				/* printable - just output the character */
				octal[0] = buf[i];
				octal[1] = '\0';
			}

			fmt = octal;
			break;
		}

		ch_len = strlen(fmt);
		if ((ccol + ch_len) >= max_cols) {
			printf("\"\n");
			ccol = 0;
			Qs = 0;
		}

		if (ccol == 0)
			printf("%s\"", prefix);

		printf("%s", fmt);
		ccol += ch_len;
	}

	if (ccol)
		printf("\"\n");
}

int main(int argc, char *argv[])
{
	uint8_t buf_chars[256*col_bytes*char_w], *p_chars = buf_chars;
	uint32_t lut[257];
	int buf_len, idx_bytes;
	int ch;

	for (ch = 0; ch < 256; ++ch) {
		int x, y, col_0 = char_w, col_l = 0;
		uint32_t cols[char_w];
		int offset;
		const unsigned char *src;

		lut[ch] = (uint32_t)(p_chars - buf_chars);

		/* special hack for SPACE: use width of 'x' */
		offset = (ch == ' ') ? ((unsigned)'x' & 0xff) : ((unsigned)ch & 0xff);
		offset = (offset / 16)*cell_h*pitch + (offset % 16)*cell_w*bpp;
		src = &gimp_image.pixel_data[offset];

		for (x = 0; x < char_w; ++x) {
			cols[x] = 0;
			for (y = 0; y < char_h; ++y) {
				/* white (well, contains red, maybe a bit of green if 16bpp) = set */
				if (src[y*pitch + x*bpp])
					cols[x] |= 1 << y;
			}

			if (cols[x]) {
				if (col_0 > x)
					col_0 = x;
				col_l = x;
			}
		}

		/* clear bits for SPACE */
		if (ch == ' ') {
			for (x = 0; x < char_w; ++x)
				cols[x] = 0;
		}

		for (x = col_0; x <= col_l; ++x) {
			p_chars = put_bytes(p_chars, cols[x], col_bytes);
		}
	}

	buf_len = (int)(p_chars - buf_chars);
	lut[256] = buf_len;
	idx_bytes = bytes_for_value(lut[256]);
	if (idx_bytes == 3) ++idx_bytes;

#define FONT_DATA_h_UUID	"1a4b0898_77a7_11e3_9c0c_0025221647f3"
	printf(
		"#ifndef FONT_DATA_h_" FONT_DATA_h_UUID "\n"
		"#define FONT_DATA_h_" FONT_DATA_h_UUID "\n"
		"\n"
	);

	printf(
		"typedef struct {\n"
		"\tuint%d_t pos[257];\n"
		"\tuint8_t data[%d];\n"
		"} font_t;\n"
		"\n",
		idx_bytes*8,
		buf_len
	);

	printf(
		"#define FONT_COL_BYTES %d\n"
		"static const font_t font = {\n"
		"\t.pos = {\n",
		col_bytes
	);

	print_ints(lut, sizeof(lut)/sizeof(*lut), "\t\t", 78 - 16);

	printf(
		"\t},\n"
		"\t.data = {\n"
	);

	print_bytes((const uint8_t*)buf_chars, buf_len, "\t\t", 78 - 16);

	printf(
		"\t},\n"
		"};\n"
		"\n"
	);

	printf(
		"#endif /* FONT_DATA_h_" FONT_DATA_h_UUID " */\n"
	);

	return 0;
}
