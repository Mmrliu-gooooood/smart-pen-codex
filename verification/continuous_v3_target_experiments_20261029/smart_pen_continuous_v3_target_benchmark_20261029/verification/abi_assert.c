#include "roi_continuous.h"
_Static_assert(sizeof(pen_roi_workspace)==21888,"core ABI");
_Static_assert(sizeof(pen_roi_refine_seed)==24,"seed ABI");
_Static_assert(PEN_ROI_REFINE_MAX_SEEDS==64,"production bound");
_Static_assert(sizeof(pen_continuous_workspace)==32640,"V3 target workspace ABI");
