#ifndef PEN_ANOTO_H
#define PEN_ANOTO_H
#include <stdint.h>
/* Canonical row-major 6x6 UP=0 LEFT=1 RIGHT=2 DOWN=3, no missing dots.
   Returns grid window origin, NOT a physical tip. Expected section mod63.
   Bounds are manifest dimensions, 6..4096. All outputs untouched on failure. */
int pen_anoto_decode(const uint8_t directions[36],uint16_t width,uint16_t height,
                     uint8_t section_u,uint8_t section_v,uint16_t *x,uint16_t *y);
#endif
