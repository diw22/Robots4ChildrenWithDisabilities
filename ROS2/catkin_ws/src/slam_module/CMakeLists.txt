cmake_minimum_required(VERSION 3.5)
project(slam_module)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)

add_executable(slam_node src/slam_node.cpp)
ament_target_dependencies(slam_node rclcpp)

install(TARGETS slam_node
  DESTINATION lib/${PROJECT_NAME}
)
install(DIRECTORY launch config
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
