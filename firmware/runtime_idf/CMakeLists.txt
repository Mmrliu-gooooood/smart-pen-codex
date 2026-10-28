cmake_minimum_required(VERSION 3.16)
set(PROJECT_VER "1") # Compile fixture only; strict signed app_desc.version policy
set(COMPONENTS main)
set(EXTRA_COMPONENT_DIRS "${CMAKE_CURRENT_LIST_DIR}/../storage" "${CMAKE_CURRENT_LIST_DIR}/../update")
include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(smartpen_runtime_compile)
