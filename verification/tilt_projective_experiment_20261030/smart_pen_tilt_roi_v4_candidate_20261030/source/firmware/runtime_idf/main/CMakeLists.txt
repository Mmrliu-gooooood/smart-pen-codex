idf_component_register(SRCS "runtime_compile_main.c" "../../runtime/contact_power.c" "../../runtime/recorder.c"
                       INCLUDE_DIRS "../../runtime" "../../portable"
                       REQUIRES storage update)
# Force adapter API bodies into the ELF so enabled configurations really link
# vendor implementations, despite app_main deliberately performing no actions.
foreach(symbol pen_storage_idf_open pen_storage_idf_begin_boot pen_storage_idf_close
               pen_storage_idf_ack pen_storage_idf_fragments pen_cp_init pen_cp_step
               pen_recorder_init pen_recorder_step
               pen_update_idf_begin pen_update_idf_write pen_update_idf_finish
               pen_update_idf_abort pen_update_idf_boot_result)
    target_link_libraries(${COMPONENT_LIB} INTERFACE "-Wl,--undefined=${symbol}")
endforeach()
