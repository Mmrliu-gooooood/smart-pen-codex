#pragma once
#include "FreeRTOS.h"
void vTaskDelay(int);
TickType_t xTaskGetTickCount(void);
BaseType_t xTaskCreatePinnedToCore(void(*)(void*),const char*,unsigned,void*,unsigned,TaskHandle_t*,int);
void vTaskDelete(TaskHandle_t);
