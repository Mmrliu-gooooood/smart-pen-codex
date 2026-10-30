idf_component_register(SRCS "partition_profile.c" "partition_profile_idf.c" "application_main.c" "board_provider_absent.c"
 "../../application/pipeline.c" "../../runtime/contact_power.c" "../../runtime/recorder.c"
 "../../vision/roi_opt.c" "../../codec/anoto.c"
 INCLUDE_DIRS "." "../../application" "../../runtime" "../../vision" "../../codec"
 REQUIRES storage esp_timer spi_flash app_update)
target_compile_options(${COMPONENT_LIB} PRIVATE -Wall -Wextra -Werror -fstack-usage)
foreach(symbol pen_application_partition_guard pen_app_init pen_app_init_replay pen_app_reclaim pen_app_needs_maintenance pen_app_prepare_replay_sleep pen_app_step pen_app_get_status pen_app_prepare_sleep pen_app_pending pen_app_offer pen_app_ack pen_roi_decode_opt
 pen_storage_idf_open pen_storage_idf_begin_boot)
 target_link_libraries(${COMPONENT_LIB} INTERFACE "-Wl,--undefined=${symbol}")
endforeach()
