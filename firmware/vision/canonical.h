#ifndef PEN_CANONICAL_H
#define PEN_CANONICAL_H
#include <stdint.h>
/* EXPERIMENTAL known-grid harness only: image exactly6*pitch square,
   canonical row order, one dot per cell, grid center pitch/2. No rotation,
   perspective, grid acquisition, mirror, occlusion/ink rejection or nib pose.
   Returns -1 rather than guessing on ambiguous centroids. */
int pen_canonical_directions(const uint8_t *gray,unsigned pitch,uint8_t out[36]);
#endif
