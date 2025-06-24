from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        #Node(
        #    package='sllidar_ros2',
        #    executable='sllidar_node',
        #    name='sllidar_node',
        #    output='screen',
        #    parameters=[{
        #        'serial_port': '/dev/lidar',
        #        'serial_baudrate': 256000,
        #        'frame_id': 'laser'
        #    }]
        #),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            arguments=['0.08', '0.005', '0.53', '0', '0', '0', 'base_link', 'laser'],
            name='laser_static_tf',
            output='screen'
        ),
        Node(
            package='kiwi_odometry',
            executable='odometry_node',
            name='kiwi_odometry_node',
            output='screen'
        )
    ])
