#ifndef TEST_ESP_PARTITION_H
#define TEST_ESP_PARTITION_H
#include <stdint.h>
#include <stdbool.h>
#include "esp_flash.h"
#define ESP_PARTITION_TYPE_ANY 0xff
#define ESP_PARTITION_SUBTYPE_ANY 0xff
#define ESP_PARTITION_TYPE_APP 0
#define ESP_PARTITION_SUBTYPE_APP_OTA_0 0x10
#define ESP_PARTITION_SUBTYPE_APP_OTA_1 0x11
typedef struct {esp_flash_t *flash_chip;uint8_t type,subtype;uint32_t address,size,erase_size;char label[17];bool encrypted,readonly;} esp_partition_t;
typedef struct mock_iterator *esp_partition_iterator_t;
esp_partition_iterator_t esp_partition_find(uint8_t,uint8_t,const char*);
const esp_partition_t *esp_partition_get(esp_partition_iterator_t);
esp_partition_iterator_t esp_partition_next(esp_partition_iterator_t);
void esp_partition_iterator_release(esp_partition_iterator_t);
#endif
