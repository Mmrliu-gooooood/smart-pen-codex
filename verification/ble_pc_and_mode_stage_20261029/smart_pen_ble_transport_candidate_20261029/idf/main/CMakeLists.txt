set(root "${CMAKE_CURRENT_LIST_DIR}/../..")
idf_component_register(SRCS "compile_main.c"
 "${root}/src/pen_ble_core.c" "${root}/src/pen_ble_actor.c" "${root}/src/pen_ble_idf.c"
 "${root}/frozen/application/pipeline.c" "${root}/frozen/runtime/contact_power.c" "${root}/frozen/runtime/recorder.c"
 "${root}/frozen/vision/roi_opt.c" "${root}/frozen/codec/anoto.c" "${root}/frozen/portable/pen.c" "${root}/frozen/storage/store.c"
 "${root}/frozen/board_provider_absent.c"
 INCLUDE_DIRS "${root}/include" "${root}/frozen" "${root}/frozen/application" "${root}/frozen/runtime"
 "${root}/frozen/vision" "${root}/frozen/codec" "${root}/frozen/portable" "${root}/frozen/storage"
 REQUIRES bt nvs_flash esp_timer)
target_compile_options(${COMPONENT_LIB} PRIVATE -Wall -Wextra -Werror -fstack-usage)
foreach(symbol pen_ble_dev_start pen_ble_dev_advertise pen_ble_dev_peer pen_ble_dev_approve pen_ble_quiesce pen_ble_resume pen_ble_transport_backend pen_ble_actor_init pen_ble_actor_turn pen_get_board_provider)
 target_link_libraries(${COMPONENT_LIB} INTERFACE "-Wl,--undefined=${symbol}")
endforeach()
