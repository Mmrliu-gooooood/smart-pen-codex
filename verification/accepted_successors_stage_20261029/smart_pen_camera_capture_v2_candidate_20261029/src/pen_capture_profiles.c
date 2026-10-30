#include "pen_capture_idf.h"
const pen_capture_profile *pen_capture_reviewed_profile(const char *name) {
 (void)name;
 /* EMPTY allowlist. No purchased SC035HGS 30-pin profile, no assumed AI pinout,
  * no unreviewed SC031GS 8mm module and no generic 24-pin mapping. */
 return NULL;
}
