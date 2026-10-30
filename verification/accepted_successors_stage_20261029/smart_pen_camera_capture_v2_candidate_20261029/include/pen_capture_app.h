#ifndef PEN_CAPTURE_APP_H
#define PEN_CAPTURE_APP_H
#include "pen_capture.h"
#include "pipeline.h"
/* Borrowed view only. Does not implement pressure ordering, decoder ROI selection,
 * physical mapper, app provider or qualification. Caller retains lease until step
 * completes and must queue contact edges independently during blocking capture. */
int pen_capture_app_frame(const pen_capture*,const pen_capture_view*,pen_app_frame*);
typedef struct {
 unsigned full_width,full_height,full_stride,left,top;
 uint64_t parent_frame_id; uint32_t source_id;
} pen_capture_roi_origin;
/* Zero-copy SOFTWARE subview only, NOT a sensor window mode. Explicit origin
 * must accompany any decoder result into physical calibration. No rescale/FOV
 * assumptions. Allowed each axis96..256 for the candidate decoder family. */
int pen_capture_app_roi(const pen_capture*,const pen_capture_view*,unsigned left,
 unsigned top,unsigned width,unsigned height,pen_app_frame*,pen_capture_roi_origin*);
void pen_capture_app_disqualify(pen_app_config*);
#endif
