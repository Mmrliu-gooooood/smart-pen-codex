set(root "${CMAKE_CURRENT_LIST_DIR}/../..")
idf_component_register(SRCS "compile_main.c" "${root}/src/pen_capture.c"
 "${root}/src/pen_capture_app.c" "${root}/src/pen_capture_idf.c" "${root}/src/pen_capture_profiles.c"
 INCLUDE_DIRS "${root}/include" "${root}/frozen/application" "${root}/frozen/runtime"
 "${root}/frozen/vision" "${root}/frozen/codec" "${root}/frozen/portable" "${root}/frozen/storage"
 REQUIRES camera_pinned esp_timer esp_psram)
target_compile_options(${COMPONENT_LIB} PRIVATE -Wall -Wextra -Werror -fstack-usage)
foreach(symbol pen_capture_idf_start pen_capture_idf_instance pen_capture_get pen_capture_release pen_capture_stop pen_capture_app_frame pen_capture_app_roi pen_capture_app_disqualify)
 target_link_libraries(${COMPONENT_LIB} INTERFACE "-Wl,--undefined=${symbol}")
endforeach()
