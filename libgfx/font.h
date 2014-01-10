#ifndef FONT_h_
#define FONT_h_ 1

#include "fb.h"

#ifdef __cplusplus
extern "C" {
#endif

int font_draw_ch(fb_t *fb, int sx, int sy, const color_t *color, int ch);
int font_draw(fb_t *fb, int sx, int sy, const color_t *color, const char *str);

#ifdef __cplusplus
};
#endif

#endif
