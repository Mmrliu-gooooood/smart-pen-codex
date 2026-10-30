set(camera "${CMAKE_CURRENT_LIST_DIR}/../../../third_party/esp32-camera")
idf_component_register(SRCS "${camera}/driver/esp_camera.c" "${camera}/driver/cam_hal.c"
 "${camera}/driver/sensor.c" "${camera}/driver/sccb-ng.c" "${camera}/sensors/sc031gs.c"
 "${camera}/target/esp32s3/ll_cam.c"
 INCLUDE_DIRS "${camera}/driver/include" "${camera}/conversions/include"
 PRIV_INCLUDE_DIRS "${camera}/driver/private_include" "${camera}/sensors/private_include" "${camera}/target/private_include"
 REQUIRES driver esp_timer nvs_flash esp_mm)

target_compile_definitions(${COMPONENT_LIB} PUBLIC PEN_CAMERA_GRAY_ONLY_BUILD=1)
