#ifndef PEN_ROI_PROJECTIVE_H
#define PEN_ROI_PROJECTIVE_H
#include "roi_continuous.h"
/* EXPERIMENTAL V4 ONLY. No camera/app integration. Pixel-centre coordinates.
 * Versioned result is incompatible with every affine mapper. No heap/RANSAC.
 * Fixed centered 80x80 crop, <=128 dots, <=256 seeds, <=25 iterations/seed.
 * All explored models must agree; this is not global homography uniqueness. */
#define PEN_PROJECTIVE_ABI 4u
#ifndef PEN_PROJECTIVE_MAX_SEEDS
#define PEN_PROJECTIVE_MAX_SEEDS 256u
#endif
typedef struct {
 pen_roi_workspace core;
 pen_roi_opt_point all[128];
 pen_roi_refine_seed seeds[PEN_PROJECTIVE_MAX_SEEDS];
 uint8_t crop[80*80];
} pen_projective_workspace;
typedef struct {
 uint32_t abi_version;
 pen_roi_opt_result roi;
 uint16_t left,top,width,height;
 double paper_to_frame[9],frame_to_paper[9];
} pen_projective_result;
typedef struct {uint32_t components,retained,coarse,seeds,iterations,models,overflow;} pen_projective_diagnostics;
int pen_roi_decode_projective_v4(const uint8_t*,size_t,unsigned,unsigned,unsigned,const pen_roi_config*,pen_projective_workspace*,pen_projective_result*,pen_projective_diagnostics*);
/* Returns 0 on nonfinite/singular denominator; never alters output on failure. */
int pen_projective_map_v4(const double h[9],double x,double y,double *u,double *v);
#endif
