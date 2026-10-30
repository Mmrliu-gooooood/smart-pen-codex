/* Compile/link fixture only. Do not flash as a usable pen application.
 * Workspace is global, not an ESP-IDF task-stack local. No camera/flash/radio
 * or decoder execution occurs here. No GPIO or power state is changed. */
#include "roi_opt.h"
#include <stdio.h>
pen_roi_workspace pen_vision_compile_workspace;
void app_main(void) {
 puts("VISION COMPILE FIXTURE ONLY: no camera, decoding, storage or radio actions");
}
