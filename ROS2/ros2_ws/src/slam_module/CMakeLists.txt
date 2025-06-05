cmake_minimum_required(VERSION 3.8)
project(slam_module)

# Enable compiler warnings
if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Required build tools and dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)

# Install launch and config directories
install(DIRECTORY launch config
  DESTINATION share/${PROJECT_NAME}
)

# Install package.xml metadata
install(FILES package.xml
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
