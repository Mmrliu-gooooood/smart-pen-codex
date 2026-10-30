#include "esp_log.h"
#include "pen_capture_idf.h"
void app_main(void) {
 /* Intentionally never call start, initialize PSRAM, run a sensor, write NVS,
  * light LEDs or register a board provider in either build configuration. */
 ESP_LOGW("pen_capture","COMPILE FIXTURE ONLY; capture OFF, approved profiles=0, mapper absent");
}
