/* Compile/link harness only. Never initializes storage, starts OTA, or drives GPIO. */
#include "esp_log.h"
void app_main(void) {
    ESP_LOGW("PEN_RUNTIME_COMPILE", "NO HARDWARE ACTIONS: compile/link harness only; no recording, OTA, camera, GPIO, erase or sleep");
    return;
}
