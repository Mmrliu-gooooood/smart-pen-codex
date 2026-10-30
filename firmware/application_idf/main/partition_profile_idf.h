#ifndef PEN_PARTITION_PROFILE_IDF_H
#define PEN_PARTITION_PROFILE_IDF_H
#include "esp_err.h"
/* Call before storage open/NVS initialisation, only after a reviewed non-NULL
 * provider is selected. Disabled profile returns NOT_SUPPORTED without reads.
 * Checks physical AND image-header size, exact full partition table and current
 * OTA application slot. Never erases, writes, programs keys or changes eFuses.
 * Passing does not approve board wiring, cell safety or a Flash manufacturer. */
esp_err_t pen_application_partition_guard(void);
#endif
