#ifndef WS28_h_bed815e4_7a46_11e3_85dd_0025221647f3
#define WS28_h_bed815e4_7a46_11e3_85dd_0025221647f3 1
/**
 * SECTION:ws28
 * @short_description: Communicate with WS2803/WS2812
 *
 * Arduino-compatible functions for sending #color_t and #fb_t to a
 * WS2803 or WS2812 LED controller chip.
 * <warning>WS2811 chips (and perhaps others) use a different signaling protocol.
 * This library will not work with those.</warning>
 */

#include "fb.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * ws28_init:
 *
 * Initialize the SPI interface for use with a WS2803 or WS2812 (not WS2811)
 */
void ws28_init(void);

/**
 * ws28_send_color:
 * @src: (in): Color to send.
 *
 * Send Red, Green, and Blue values to the WS28xx, in that order, not pausing for a reset.
 *
 * See also: ws28_send(), SPI.transfer()
 */
void ws28_send_color(const color_t *src);

/**
 * ws28_send:
 * @fb: (in): Framebuffer to send.
 *
 * Send an entire #fb_t to the WS28xx, pausing before send if necessary
 * to reset the WS28xx's to the first pixel.
 *
 * The pixels are sent in <emphasis>column-major</emphasis> order; i.e., all the pixels with x==0 are sent, then all with x==1, etc.
 */
void ws28_send(fb_t *fb);

#ifdef __cplusplus
};
#endif

#endif
