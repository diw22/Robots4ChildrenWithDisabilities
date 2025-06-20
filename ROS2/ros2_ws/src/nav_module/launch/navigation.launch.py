from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # Declare launch configurations
    map_yaml = LaunchConfiguration('map')
    config_dir = LaunchConfiguration('config_dir')
    rviz_config = LaunchConfiguration('rviz_config')

    # Resolve config directory as path within the package
    config_path = PathJoinSubstitution([
        FindPackageShare('nav_module'),
        config_dir
    ])

    return LaunchDescription([
        DeclareLaunchArgument(
            'map',
            default_value='/home/raspi/my_map.yaml',
            description='Full path to the map YAML file to load'
        ),
        DeclareLaunchArgument(
            'config_dir',
            default_value='config/',
            description='Relative path to the config directory inside the package'
        ),
        DeclareLaunchArgument(
            'rviz_config',
            default_value='/home/raspi/.rviz/map.rviz',
            description='Full path to the RViz config file'
        ),

        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            parameters=[{'yaml_filename': map_yaml}],
            output='screen'
        ),

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

        # Lifecycle Manager
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
                    'bt_navigator',
                    'behavior_server'
                ]
            }]
        ),
    ])
