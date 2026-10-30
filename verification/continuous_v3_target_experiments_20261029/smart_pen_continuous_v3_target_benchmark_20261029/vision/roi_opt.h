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
/* Winning fitted grid. Origin is decoded (x,y) paper cell in image pixel-center
 * coordinates. Step vectors map +1 paper cell along each axis. Diagnostic
 * orthogonal model only; NOT nib pose or calibration. */
typedef struct {
 double origin_x,origin_y,x_dx,x_dy,y_dx,y_dy;
} pen_roi_grid_transform;
/* Identical search/result contract; optional transform remains untouched on
 * failure. Existing pen_roi_decode_opt ABI and behavior remain unchanged. */
int pen_roi_decode_opt_transform(const uint8_t *gray,size_t length,unsigned width,unsigned height,
 unsigned stride,const pen_roi_config *config,pen_roi_workspace *workspace,
 pen_roi_prior *prior,pen_roi_opt_result *result,pen_roi_grid_transform *transform);
/* Returns original PEN_ROI_* codes, every failure preserves result, clears prior.
 * Prior NULL allowed. Warm miss falls back to bounded cold acquisition.
 * Orthogonal nonuniform grid, NOT general affine/homography/perspective.
 * Cold: angle -60..60 step2, x pitch8..32 step.5, y/x .6..1.4 step.1.
 */
int pen_roi_decode_opt(const uint8_t *gray,size_t length,unsigned width,unsigned height,
 unsigned stride,const pen_roi_config *config,pen_roi_workspace *workspace,
 pen_roi_prior *prior,pen_roi_opt_result *result);
/* V3 experimental cold augmentation. Original APIs above remain unchanged.
 * Caller supplies MAX_SEEDS records; no aliasing with workspace/input/outputs.
 * Every qualified coarse initializer is considered; overflow fails AMBIGUOUS.
 * Original strict validation/consensus gates are never relaxed. Diagnostics
 * are explicitly overwritten on EVERY call (including failure), unlike result
 * and transform, which remain untouched on failure. No fake/warm prior API. */
#ifndef PEN_ROI_REFINE_MAX_SEEDS
#define PEN_ROI_REFINE_MAX_SEEDS 64u
#endif
typedef struct { double pitch,angle,ratio; } pen_roi_refine_seed;
typedef struct { uint32_t cold_candidates,seeds,iterations,refined_models; } pen_roi_refine_diagnostics;
int pen_roi_decode_refined_transform(const uint8_t *gray,size_t length,unsigned width,unsigned height,
 unsigned stride,const pen_roi_config *config,pen_roi_workspace *workspace,pen_roi_refine_seed *seeds,
 pen_roi_opt_result *result,pen_roi_grid_transform *transform,pen_roi_refine_diagnostics *diagnostics);
#endif
