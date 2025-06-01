cmake_minimum_required(VERSION 3.5)
project(rplidar_ros2)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)

add_executable(rplidar_node src/rplidar_node.cpp)
ament_target_dependencies(rplidar_node rclcpp)

install(TARGETS rplidar_node
  DESTINATION lib/${PROJECT_NAME}
)
install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
