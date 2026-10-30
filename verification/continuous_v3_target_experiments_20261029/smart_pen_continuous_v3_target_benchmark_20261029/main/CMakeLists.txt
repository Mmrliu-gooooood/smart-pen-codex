idf_component_register(SRCS "bench_main.c" "trace.c" "../vision/roi_continuous.c" "../vision/roi_opt.c" "../codec/anoto.c" "../legacy/vision/roi_opt.c"
 INCLUDE_DIRS "." "../vision" "../codec" REQUIRES esp_timer)
set_source_files_properties("../legacy/vision/roi_opt.c" PROPERTIES COMPILE_DEFINITIONS "pen_roi_decode_opt=pen_roi_decode_opt_frozen")
target_compile_options(${COMPONENT_LIB} PRIVATE -Wall -Wextra -Werror -fstack-usage)

target_link_libraries(${COMPONENT_LIB} INTERFACE "-Wl,--wrap=pen_roi_decode_refined_transform")
