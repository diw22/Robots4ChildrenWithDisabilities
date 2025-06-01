cmake_minimum_required(VERSION 3.5)
project(system_launcher)

find_package(ament_cmake REQUIRED)

install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
