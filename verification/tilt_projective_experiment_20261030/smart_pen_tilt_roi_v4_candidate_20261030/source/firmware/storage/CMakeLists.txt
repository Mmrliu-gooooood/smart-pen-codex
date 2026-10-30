idf_component_register(SRCS "store.c" "storage_idf.c" "../portable/pen.c"
 INCLUDE_DIRS "." "../portable" REQUIRES esp_partition nvs_flash)
