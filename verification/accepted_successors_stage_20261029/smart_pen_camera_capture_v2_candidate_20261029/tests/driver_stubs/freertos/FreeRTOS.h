#pragma once
#include <stdint.h>
#include "sdkconfig.h"
#include "esp_idf_version.h"
#define IRAM_ATTR
#define DRAM_STR(s) (s)
typedef int BaseType_t; typedef unsigned UBaseType_t; typedef uint32_t TickType_t; typedef int portMUX_TYPE;
typedef void *TaskHandle_t; typedef void *QueueHandle_t; typedef void *intr_handle_t;
#define portMUX_INITIALIZER_UNLOCKED 0
#define portENTER_CRITICAL(x) ((void)(x))
#define portEXIT_CRITICAL(x) ((void)(x))
#define pdTRUE 1
#define pdFALSE 0
#define pdPASS 1
#define portMAX_DELAY UINT32_MAX
#define portTICK_PERIOD_MS 1
#define pdMS_TO_TICKS(x) (x)
#define configMAX_PRIORITIES 25
