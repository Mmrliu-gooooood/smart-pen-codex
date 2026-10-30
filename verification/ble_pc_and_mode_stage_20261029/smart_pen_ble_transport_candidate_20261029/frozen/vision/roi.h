#ifndef PEN_ROI_H
#define PEN_ROI_H
#include <stddef.h>
#include <stdint.h>
/* Experimental bounded small-ROI acquisition, not a camera/nib pose driver.
 * Gray8, <=256x256, stride>=width. Heap workspace <=64 KiB, plus fixed stack arrays.
 * Complete isolated dark dots; nominal 1/6-cell offsets, pitch 8..32 px,
 * orientation within +/-20 degrees of canonical (no quadrant/mirror search).
 * Square similarity grid only; perspective beyond residual gates is rejected.
 * Config describes paper bounds/section, NEVER known image cell coordinates.
 * Success is a decoded WINDOW ORIGIN, not VALID pen pose or physical ink.
 * Output untouched on every failure. No missing-dot prediction/correction.
 */
typedef struct { uint16_t paper_width, paper_height; uint8_t section_u, section_v; } pen_roi_config;
typedef struct {
 uint16_t x, y; /* decoded window origin in paper cells */
 uint16_t dots, windows;
 float pitch_px, angle_deg, residual_cells;
 uint8_t directions[36];
} pen_roi_result;
enum { PEN_ROI_OK=0, PEN_ROI_ARGUMENT=-1, PEN_ROI_DETECTION=-2,
       PEN_ROI_NO_GRID=-3, PEN_ROI_AMBIGUOUS=-4, PEN_ROI_MEMORY=-5 };
int pen_roi_decode(const uint8_t *gray,size_t length,unsigned width,unsigned height,
                   unsigned stride,const pen_roi_config *config,pen_roi_result *result);
#endif
