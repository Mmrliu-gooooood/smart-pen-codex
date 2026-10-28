idf_component_register(SRCS "vision_compile_main.c" "../../vision/roi_opt.c" "../../codec/anoto.c"
                       INCLUDE_DIRS "../../vision" "../../codec")
target_compile_options(${COMPONENT_LIB} PRIVATE -Wall -Wextra -Werror -fstack-usage)
foreach(symbol pen_roi_decode_opt pen_anoto_decode pen_vision_compile_workspace)
 target_link_libraries(${COMPONENT_LIB} INTERFACE "-Wl,--undefined=${symbol}")
endforeach()
