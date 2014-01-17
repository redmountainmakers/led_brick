#ifndef WS28_h_bed815e4_7a46_11e3_85dd_0025221647f3
#define WS28_h_bed815e4_7a46_11e3_85dd_0025221647f3 1

#include "fb.h"

#ifdef __cplusplus
extern "C" {
#endif

/* initialize SPI interface */
void ws28_init(void);

/* Send a single color to SPI-connected ws28xx */
void ws28_send_color(const color_t *src);

/* Send the framebuffer to SPI-connected ws28xx */
void ws28_send(fb_t *fb);

#ifdef __cplusplus
};
#endif

#endif
