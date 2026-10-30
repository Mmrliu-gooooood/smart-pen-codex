#ifndef PEN_ROI_CONTINUOUS_H
#define PEN_ROI_CONTINUOUS_H
#include "roi_opt.h"
/* EXPERIMENTAL pixel-only central ROI policy; not camera/tip qualification.
 * Canonical Gray8 frame: 96..256 each dimension, no resize, positive stride.
 * One 96px crop; only excessive interior component count permits an 80px crop.
 * Border-connected components removed only if <=24px, extent <=6px,
 * inward depth <=4px. Dot-sized ink cannot be distinguished by this policy.
 * Requires 36..100 retained dots; original core remains capped at 128.
 * One full cold search plus <=64 current-pixel continuous refinements.
 * No prior/cached coordinates, no decode-driven ROI retry.
 * Evidence outside the selected ROI is not checked. Reject != no paper present.
 * Coordinates are paper WINDOW/grid diagnostics, never physical nib or VALID.
 * No heap; caller-owned workspace must NOT be on a default small task stack.
 * No aliasing between frame/config/workspace/output; no concurrent workspace use.
 */
#define PEN_CONTINUOUS_ROI_MAX_SIDE 96u
#define PEN_CONTINUOUS_ROI_MAX_DOTS 100u
#define PEN_CONTINUOUS_EDGE_MAX_PIXELS 24u
#define PEN_CONTINUOUS_EDGE_MAX_EXTENT 6u
#define PEN_CONTINUOUS_EDGE_MAX_DEPTH 4u
typedef struct {
 pen_roi_workspace core;
 pen_roi_refine_seed seeds[PEN_ROI_REFINE_MAX_SEEDS];
 uint8_t crop[PEN_CONTINUOUS_ROI_MAX_SIDE*PEN_CONTINUOUS_ROI_MAX_SIDE];
} pen_continuous_workspace;
typedef struct {
 pen_roi_opt_result roi;
 uint16_t left,top,width,height;
 uint16_t edge_components,edge_pixels;
 uint8_t crop_attempts;
 /* [a,b,tx,c,d,ty]: (u,v)=(a*x+b*y+tx,c*x+d*y+ty).
  * Frame and crop use integer pixel-center coordinates, top-left +y down.
  * frame=crop+(left,top). Paper uses continuous encoded cell coordinates.
  * These invert the FITTED orthogonal model; not a calibrated homography. */
 double paper_to_frame[6],frame_to_paper[6];
 /* V3-only result ABI: do not cast to the frozen V2 result. */
 uint16_t refine_seeds,refine_iterations,refine_models;
} pen_continuous_result;
/* Original PEN_ROI status codes. Every failure preserves all output bytes.
 * DETECTION includes crop selection, contrast, excessive density/component,
 * too few complete dots, and original detector rejection. NO_GRID/AMBIGUOUS
 * preserve core meaning; no alternate crop is tried after either status.
 */
int pen_roi_decode_continuous(const uint8_t *gray,size_t length,unsigned width,unsigned height,
 unsigned stride,const pen_roi_config *config,pen_continuous_workspace *workspace,
 pen_continuous_result *result);
#endif
