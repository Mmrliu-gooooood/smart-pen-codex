/* Compile-only target ABI proof, not executed or linked into benchmark. */
#include "roi_continuous.h"
_Static_assert(sizeof(pen_roi_workspace)==21888, "Unexpected target core workspace layout");
_Static_assert(sizeof(pen_continuous_workspace)==31104, "Unexpected target continuous workspace layout");
_Static_assert(_Alignof(pen_continuous_workspace)<=8, "Heap allocator alignment assumptions changed");
