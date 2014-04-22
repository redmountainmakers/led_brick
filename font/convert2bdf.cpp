/*
	convert2bdf.c - convert a bitmap font to BDF format.
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

#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <opencv2/opencv.hpp>

static IplImage *img;

#define bpp (3)
#define pitch (img->widthStep)
#define cell_w (img->width / 16)
#define cell_h (img->height / 16)
#define char_w (cell_w - 1)
#define char_h (cell_h - 1)
#define col_bytes ((char_h + 7) / 8)
#define idata (img->imageData)

static inline uint8_t *put_bytes(uint8_t *p, uint32_t val, int bytes)
{
	while (bytes--) {
		*p++ = val & 0xff;
		val >>= 8;
	}
	return p;
}

int main(int argc, char *argv[])
{
	uint8_t *buf_chars, *p_chars;
	uint32_t lut[257];
	int buf_len;
	int ch;
	int i, j, k;

	if (argc <= 1) {
		fprintf(stderr, "%s <image>\n", argv[0]);
		return -1;
	}

	img = cvLoadImage(argv[1]);
	if (!img) {
		fprintf(stderr, "Couldn't open %s\n", argv[1]);
		return -1;
	}

	buf_chars = new uint8_t[256*col_bytes*char_w];
	p_chars = buf_chars;

	for (ch = 0; ch < 256; ++ch) {
		int x, y, col_0 = char_w, col_l = 0;
		uint32_t cols[char_w];
		int offset;
		const unsigned char *src;

		lut[ch] = (uint32_t)(p_chars - buf_chars);

		/* special hack for SPACE: use width of 'x' */
		offset = (ch == ' ') ? ((unsigned)'x' & 0xff) : ((unsigned)ch & 0xff);
		offset = (offset / 16)*cell_h*pitch + (offset % 16)*cell_w*bpp;
		src = (unsigned char *)&idata[offset];

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

	printf(
		"STARTFONT 2.1\n"
		"FONT -rmm-%dx%d-medium-r-normal--%d-160-75-75-c-80-cp437\n"
		"SIZE %d 75 75\n"
		"FONTBOUNDINGBOX %d %d 0 0\n"
		"STARTPROPERTIES 3\n"
		"COPYRIGHT 2014, Red Mountain Makers. GNU GPLv3 or later.\n"
		"FONT_ASCENT %d\n"
		"FONT_DESCENT 1\n"
		"ENDPROPERTIES\n"
		"CHARS 256\n",
		char_h, char_h, char_h, char_h, char_w, char_h, char_h
	);
		
	for (i = 0; i < 256; ++i) {
		printf(
			"STARTCHAR %d\n"
			"ENCODING %d\n"
			"DWIDTH %d 0\n"
			"BBX %d %d 0 -1\n"
			"BITMAP\n",
			i, i, lut[i+1] - lut[i] + 1, lut[i+1] - lut[i], char_h
		);

		for (j = 0; j < char_h; ++j) {
			uint32_t row = 0;
			int len = lut[i+1] - lut[i], plen;
			plen = (len + 7) & ~7;

			for (k = lut[i]; k < lut[i+1]; ++k) {
				row <<= 1;
				row |= !!(buf_chars[k] & (1 << j));
			}

			row <<= (plen - len);
			printf("%0*X\n", 2*(plen / 8), row);
		}

		printf("ENDCHAR\n");
	}
	printf("ENDFONT\n");

	/*delete buf_chars;*/
	return 0;
}
