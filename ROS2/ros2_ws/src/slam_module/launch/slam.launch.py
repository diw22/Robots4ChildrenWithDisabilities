from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    # SLAM Toolbox
    slam_toolbox_dir = get_package_share_directory('slam_toolbox')
    slam_launch_file = os.path.join(slam_toolbox_dir, 'launch', 'online_async_launch.py')
    slam_params = '/home/raspi/Robots4ChildrenWithDisabilities/ROS2/ros2_ws/src/slam_module/config/slam_toolbox_params.yaml'

    return LaunchDescription([

        # 1. Lidar Node: publishes /scan
        Node(
            package='sllidar_ros2',
            executable='sllidar_node',
            name='sllidar_node',
            output='screen',
            parameters=[
                {'serial_port': '/dev/lidar'},
                {'serial_baudrate': 256000},
                {'frame_id': 'laser'},
                {'inverted': False},
                {'angle_compensate': True},
                {'scan_mode': 'Standard'},
                {'force_scan': True}
            ]
        ),

        # 2. Static Transform: base_link → laser
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='laser_tf',
            arguments=['0.08', '0.005', '0.53', '0', '0', '0', 'base_link', 'laser']
        ),

        # 3. Odometry Node: odom → base_link
        Node(
            package='kiwi_odometry',
            executable='odometry_node',
            name='kiwi_odometry_node',
            output='screen'
        ),

        # 4. SLAM Toolbox: mapping mode
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(slam_launch_file),
            launch_arguments={
                'slam_params_file': slam_params,
                'use_sim_time': 'false',
                'mode': 'mapping'
            }.items()
        )
    ])
