idf_component_register(SRCS "update_policy.c" "update_idf.c" INCLUDE_DIRS "."
                       REQUIRES app_update esp_app_format nvs_flash mbedtls)
