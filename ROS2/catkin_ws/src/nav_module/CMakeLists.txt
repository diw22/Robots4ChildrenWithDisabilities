cmake_minimum_required(VERSION 3.5)
project(nav_module)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)

add_executable(navigator_node src/navigator_node.cpp)
ament_target_dependencies(navigator_node rclcpp)

install(TARGETS navigator_node
  DESTINATION lib/${PROJECT_NAME}
)
install(DIRECTORY launch config
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
