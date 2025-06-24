from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='nav_module',
            executable='navigator_node',
            name='navigator_node',
            output='screen'
        ),
        ExecuteProcess(
            cmd=['python3', '/home/raspi/Robots4ChildrenWithDisabilities/ROS2/ros2_ws/src/nav_module/src/cmd_vel_bridge.py'],
            name='cmd_vel_bridge',
            output='screen'
        )
    ])
