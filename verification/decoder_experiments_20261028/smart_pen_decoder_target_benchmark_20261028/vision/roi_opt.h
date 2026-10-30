#ifndef PEN_ROI_OPT_H
#define PEN_ROI_OPT_H
#include "roi.h"
/* EXPERIMENTAL optimized candidate, separate from roi.c reference.
 * Caller owns workspace (static/arena; NOT a default small task stack).
 * No malloc/free. A workspace cannot be used concurrently/reentrantly.
 * Prior is only a search hint, never substitutes for current pixel decoding.
 * WARM SUCCESS CHECKS LOCAL CANDIDATES ONLY, not cold global uniqueness.
 * An unsearched conflicting model can be missed; not safety-equivalent to
 * exhaustive cold acquisition. For full search pass prior=NULL.
 * Result remains a paper WINDOW origin, never a physical nib/ink VALID flag.
 */
typedef struct { double x,y; } pen_roi_opt_point;
typedef struct {
 uint8_t seen[256*256/8]; uint32_t queue[256];
 pen_roi_opt_point points[128];
 double u[128],v[128],xx[128],yy[128];
 uint8_t dirs[128]; int grid[40*40];
} pen_roi_workspace;
typedef struct {
 uint32_t valid; /* 0 or 1; other values ignored as invalid hints */
 float pitch_px, angle_deg, y_scale;
} pen_roi_prior;
typedef struct {
 pen_roi_result decoded;
 float y_scale;
 uint32_t candidates;
 uint8_t used_warm_start;
} pen_roi_opt_result;
/* Returns original PEN_ROI_* codes, every failure preserves result, clears prior.
 * Prior NULL allowed. Warm miss falls back to bounded cold acquisition.
 * Orthogonal nonuniform grid, NOT general affine/homography/perspective.
 * Cold: angle -60..60 step2, x pitch8..32 step.5, y/x .6..1.4 step.1.
 */
int pen_roi_decode_opt(const uint8_t *gray,size_t length,unsigned width,unsigned height,
 unsigned stride,const pen_roi_config *config,pen_roi_workspace *workspace,
 pen_roi_prior *prior,pen_roi_opt_result *result);
#endif
