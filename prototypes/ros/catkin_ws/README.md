# ROS-based Robot System

This directory contains all ROS components for robot navigation using Lidar and SLAM.

## Structure
- `rplidar_ros/`: Lidar sensor driver
- `slam_module/`: SLAM setup using gmapping
- `nav_module/`: Navigation stack with move_base and AMCL
- `system_launcher/`: Full system launch integration + RViz configs

## How to Run
1. `cd catkin_ws && catkin_make`
2. `source devel/setup.bash`
3. `roslaunch system_launcher/system.launch`
