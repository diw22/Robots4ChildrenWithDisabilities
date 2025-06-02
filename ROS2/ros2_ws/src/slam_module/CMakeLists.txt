cmake_minimum_required(VERSION 3.8)
project(slam_module)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)

add_executable(slam_node src/slam_node.cpp)
ament_target_dependencies(slam_node rclcpp)

install(TARGETS slam_node
  DESTINATION lib
)
install(DIRECTORY launch config
  DESTINATION share/${PROJECT_NAME}
)
install(FILES package.xml
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
