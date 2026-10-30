idf_component_register(SRCS "bench_main.c" "bench_wire.c" "../../portable/pen.c"
    INCLUDE_DIRS "../../portable" REQUIRES bt nvs_flash esp_timer)
