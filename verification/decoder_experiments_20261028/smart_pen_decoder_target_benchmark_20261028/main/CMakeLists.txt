idf_component_register(SRCS "bench_main.c" "../vision/roi_opt.c" "../codec/anoto.c"
 INCLUDE_DIRS "." "../vision" "../codec" REQUIRES esp_timer)
target_compile_options(${COMPONENT_LIB} PRIVATE -Wall -Wextra -Werror -fstack-usage)
