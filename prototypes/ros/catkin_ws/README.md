# ROS Workspace for Robot Navigation & Vision

This workspace is part of the **Robots4ChildrenWithDisabilities** project, and it contains all ROS packages related to navigation, SLAM, and computer vision.

## 🛠 Development Environment

This ROS workspace is developed and tested under the following environment:

- **ROS version:** ROS Noetic Ninjemys (ROS 1)
- **Operating system:** Ubuntu 20.04 LTS (Focal Fossa)
- **Platform:** Linux-based (tested on WSL2 and native Ubuntu)
- **Catkin workspace:** Standard `catkin_ws` structure
- **Python version:** Python 3.8+
- **C++ version:** C++14 (default in ROS Noetic)
- **Visualization tools:** RViz
- **Launch system:** `roslaunch` with modular package integration

> 📌 Note: ROS Noetic is the final official distribution of ROS 1 and is designed to run on Ubuntu 20.04.  
> Please ensure you're using this OS and ROS version to avoid compatibility issues.

## 📁 Workspace Structure

```text
catkin_ws/
├── src/
│   ├── rplidar_ros/         # ROS driver for the A2M12 2D Lidar sensor
│   ├── slam_module/         # SLAM configuration and launch files using gmapping
│   ├── nav_module/          # Navigation stack setup (move_base, AMCL, costmaps)
│   ├── oakd_module/         # Object detection and image recognition with OAK-D camera
│   └── system_launcher/     # Main launch file to bring everything together
├── README.md                # This file — workspace overview
└── .gitignore               # Ignores build/ and devel/ folders from Git
``` 

## 📦Package Descriptions
### `rplidar_ros/`
Contains the driver for the RPLIDAR A2M12 2D Lidar. Publishes `/scan` data used for SLAM and obstacle avoidance.

### `slam_module/`
Responsible for mapping the environment using the Lidar data via `gmapping`. Includes launch files and SLAM parameter configs.

### `nav_module/`
Implements autonomous navigation using `move_base`, `AMCL`, and costmaps. Calculates safe paths on the generated map.

### `oakd_module/`
Handles computer vision tasks using the OAK-D camera. Includes:
- `launch/`: launch files for running the camera and vision nodes
- `scripts/`: Python nodes for object detection, recognition, etc.
- `config/`: settings for YOLO models, camera parameters, topics

### `system_launcher/`
A central package that contains a unified `system.launch` file which starts all other modules. Also contains RViz configuration files for visualization.

---

## 👩‍💻 How to Write ROS Nodes in Python or C++ 
### 🔹 Python (Python 3.8) 
- Files end with `.py` and are placed in your package's `scripts/` folder.
- Start your Python files with: ``` #!/usr/bin/env python3 ``` (This tells ROS to run it with Python 3 interpreter)
- Make the script executable (so ROS can run it like a program):
```python
chmod +x your_script.py
```
- Run the Python ROS node:
```python
rosrun [your_package] [your_script.py]
# e.g. rosrun oakd_module object_tracker.py
```
---
### 🔹 C++ (C++14) 
- Files end with `.cpp` and go inside your package's `src/` folder.
- Update CMakeLists.txt to compile your C++ node.
- Build your workspace:
```bash
cd ~/Robots4ChildrenWithDisabilities/prototypes/ros/catkin_ws
catkin_make
```
- Run the C++ ROS node:
```bash
rosrun [your_package] [your_executable]
# e.g. rosrun nav_module path_planner
```
>💡 Tip: Python is good for quick scripts. Use C++ for performance-heavy tasks.

---

## 💻 Using VSCode with ROS
### 🧩 Recommended Extensions: 
- ms-iot.vscode-ros (official ROS support)
- ms-python.python (Python language tools)
- ms-vscode.cpptools (C++ IntelliSense & debugging)

### 🚀 How to Open Your Workspace: 
```bash
code ~/Robots4ChildrenWithDisabilities/prototypes/ros/catkin_ws
```

## 🧪 How to Build & Run

```bash
cd ~/catkin_ws
catkin_make
source devel/setup.bash
roslaunch system_launcher/system.launch
