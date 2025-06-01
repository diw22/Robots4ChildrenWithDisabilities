# generated from ament/cmake/core/templates/nameConfig.cmake.in

# prevent multiple inclusion
if(_system_launcher_CONFIG_INCLUDED)
  # ensure to keep the found flag the same
  if(NOT DEFINED system_launcher_FOUND)
    # explicitly set it to FALSE, otherwise CMake will set it to TRUE
    set(system_launcher_FOUND FALSE)
  elseif(NOT system_launcher_FOUND)
    # use separate condition to avoid uninitialized variable warning
    set(system_launcher_FOUND FALSE)
  endif()
  return()
endif()
set(_system_launcher_CONFIG_INCLUDED TRUE)

# output package information
if(NOT system_launcher_FIND_QUIETLY)
  message(STATUS "Found system_launcher: 0.0.1 (${system_launcher_DIR})")
endif()

# warn when using a deprecated package
if(NOT "" STREQUAL "")
  set(_msg "Package 'system_launcher' is deprecated")
  # append custom deprecation text if available
  if(NOT "" STREQUAL "TRUE")
    set(_msg "${_msg} ()")
  endif()
  # optionally quiet the deprecation message
  if(NOT system_launcher_DEPRECATED_QUIET)
    message(DEPRECATION "${_msg}")
  endif()
endif()

# flag package as ament-based to distinguish it after being find_package()-ed
set(system_launcher_FOUND_AMENT_PACKAGE TRUE)

# include all config extra files
set(_extras "")
foreach(_extra ${_extras})
  include("${system_launcher_DIR}/${_extra}")
endforeach()
