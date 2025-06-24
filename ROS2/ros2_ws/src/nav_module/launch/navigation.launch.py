from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, TimerAction
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    # Declare launch configurations
    map_yaml = LaunchConfiguration('map')
    config_dir = LaunchConfiguration('config_dir')
    rviz_config = LaunchConfiguration('rviz_config')

    config_path = PathJoinSubstitution([
        FindPackageShare('nav_module'),
        config_dir
    ])

    return LaunchDescription([
        # ──────────────────────── Launch Arguments ────────────────────────
        DeclareLaunchArgument(
            'map',
            default_value='/home/raspi/Robots4ChildrenWithDisabilities/ROS2/ros2_ws/test_map.yaml',
            description='Full path to the map YAML file to load'
        ),
        DeclareLaunchArgument(
            'config_dir',
            default_value='config/',
            description='Relative path to the config directory inside the package'
        ),
        DeclareLaunchArgument(
            'rviz_config',
            default_value='/home/raspi/.rviz2/map.rviz',
            description='Full path to the RViz config file'
        ),

        # ──────────────────────── Core Sensor Nodes ────────────────────────
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
        ),

        # ──────────────────────── Navigation Stack ────────────────────────
        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            parameters=[{'yaml_filename': map_yaml}],
            output='screen'
        ),

        TimerAction(
            period=5.0,
            actions=[
                Node(
                    package='nav2_amcl',
                    executable='amcl',
                    name='amcl',
                    parameters=[PathJoinSubstitution([config_path, 'amcl.yaml'])],
                    output='screen'
                ),

                Node(
                    package='nav2_planner',
                    executable='planner_server',
                    name='planner_server',
                    parameters=[
                        PathJoinSubstitution([config_path, 'move_base.yaml']),
                        PathJoinSubstitution([config_path, 'global_costmap.yaml']),
                        PathJoinSubstitution([config_path, 'costmap_common.yaml'])
                    ],
                    output='screen'
                ),

                Node(
                    package='nav2_controller',
                    executable='controller_server',
                    name='controller_server',
                    parameters=[
                        PathJoinSubstitution([config_path, 'move_base.yaml']),
                        PathJoinSubstitution([config_path, 'local_costmap.yaml']),
                        PathJoinSubstitution([config_path, 'costmap_common.yaml'])
                    ],
                    output='screen'
                ),

                Node(
                    package='nav2_bt_navigator',
                    executable='bt_navigator',
                    name='bt_navigator',
                    parameters=[PathJoinSubstitution([config_path, 'move_base.yaml'])],
                    output='screen'
                ),

                Node(
                    package='nav2_behaviors',
                    executable='behavior_server',
                    name='behavior_server',
                    parameters=[PathJoinSubstitution([config_path, 'move_base.yaml'])],
                    output='screen'
                ),

                Node(
                    package='nav2_lifecycle_manager',
                    executable='lifecycle_manager',
                    name='lifecycle_manager_navigation',
                    output='screen',
                    parameters=[{
                        'autostart': True,
                        'node_names': [
                            'map_server',
                            'amcl',
                            'planner_server',
                            'controller_server',
                            'behavior_server',
                            'bt_navigator'
                        ]
                    }]
                )
            ]
        ),


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
        ),

        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config],
            output='screen'
        ),
    ])
