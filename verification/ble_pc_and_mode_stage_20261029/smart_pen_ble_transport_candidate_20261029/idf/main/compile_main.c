#include "esp_log.h"
#include "board_provider.h"
/* Intentionally identical behavior in every build configuration. No radio,
 * NVS, storage, sensor, GPIO, pairing, automatic advertising or task start. */
void app_main(void){
 ESP_LOGW("ble_compile", "COMPILE ONLY: provider remains NULL; no hardware APIs called");
 (void)pen_get_board_provider();
}
