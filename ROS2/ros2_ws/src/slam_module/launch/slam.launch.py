from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    # Path to the official SLAM Toolbox launch file
    slam_toolbox_dir = get_package_share_directory('slam_toolbox')
    slam_launch_file = os.path.join(slam_toolbox_dir, 'launch', 'online_async_launch.py')

    # Path to the slam_toolbox parameter file (update if moved)
    slam_params = '/home/raspi/Robots4ChildrenWithDisabilities/ROS2/ros2_ws/src/slam_module/config/slam_toolbox_params.yaml'

    return LaunchDescription([
        # Static Transform Publisher: base_link → laser
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='laser_tf',
            arguments=['0.1', '0', '0.08', '0', '0', '0', 'base_link', 'laser']
        ),

        # Include SLAM Toolbox official launch file
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(slam_launch_file),
            launch_arguments={
                'slam_params_file': slam_params,
                'use_sim_time': 'false',
                'mode': 'mapping'
            }.items()
        )
    ])
