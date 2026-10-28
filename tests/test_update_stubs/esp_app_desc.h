#ifndef MOCK_APP_DESC_H
#define MOCK_APP_DESC_H
#include <stdint.h>
typedef struct {uint32_t secure_version;char version[32];char project_name[32];} esp_app_desc_t;
const esp_app_desc_t *esp_app_get_description(void);
#endif
