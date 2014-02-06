#ifndef FONT_h_
#define FONT_h_ 1
/**
 * SECTION:font
 * @short_description: Basic font drawing support.
 *
 * Contains functions for drawing characters and strings to a #fb_t.
 *
 * <note>These function draw <emphasis>inside</emphasis> the framebuffer only.
 * They will skip drawing locations outside the framebuffer,
 * so you can use them to scroll text off-screen.</note>
 *
 * <note>The background is not drawn by these functions.</note>
 */

#include "fb.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * font_draw_ch:
 * @fb: (in): The framebuffer to draw in.
 * @sx: (in): Left starting location of the character.
 * @sy: (in): Top starting location of the character.
 * @color: (in): Color to draw with.
 * @ch: (in): Character to draw in @fb at @sx,@sy with color @color.
 *
 * Draw a single character in a framebuffer.
 *
 * Returns: Number of columns the character takes, including a spacer column.
 *
 * See also: font_draw()
 */
int font_draw_ch(fb_t *fb, int sx, int sy, const color_t *color, int ch);

/**
 * font_draw:
 * @fb: (in): The framebuffer.
 * @sx: (in): Left starting location of the character.
 * @sy: (in): Top starting location of the character.
 * @color: (in): Color to draw with.
 * @str: (in) (array null-terminated=1): String to draw in @fb at @sx,@sy with color @color.
 *
 * Draw a string in a framebuffer.
 *
 * Returns: Number of columns the string takes, including a spacer column.
 */
int font_draw(fb_t *fb, int sx, int sy, const color_t *color, const char *str);

#ifdef __cplusplus
};
#endif

#endif
