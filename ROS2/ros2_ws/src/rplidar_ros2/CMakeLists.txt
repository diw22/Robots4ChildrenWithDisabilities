cmake_minimum_required(VERSION 3.8)
project(rplidar_ros2)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)

add_executable(rplidar_node src/rplidar_node.cpp)
ament_target_dependencies(rplidar_node rclcpp)

install(TARGETS rplidar_node
  DESTINATION lib
)
install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)
install(FILES package.xml
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
