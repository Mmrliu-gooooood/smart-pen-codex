#ifndef PEN_CAPTURE_IDF_H
#define PEN_CAPTURE_IDF_H
#include "pen_capture.h"
/* Singleton LCD_CAM owner. Construction/start must be serial, no other camera
 * client allowed. No real board profile is registered. compile-enable is not run. */
const pen_capture_profile *pen_capture_reviewed_profile(const char *name);
pen_capture *pen_capture_idf_instance(void);
int pen_capture_idf_start(const char *profile_name,int explicit_runtime_enable);
#endif
