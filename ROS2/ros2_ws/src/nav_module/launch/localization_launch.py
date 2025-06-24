from launch import LaunchDescription
from launch.actions import RegisterEventHandler, TimerAction
from launch.event_handlers import OnProcessStart
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    config_path = PathJoinSubstitution([
        FindPackageShare('nav_module'),
        'config'
    ])

    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        parameters=[{'yaml_filename': '/home/raspi/Robots4ChildrenWithDisabilities/ROS2/ros2_ws/test_map.yaml'}],
        output='screen'
    )

    amcl = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        parameters=[config_path + '/amcl.yaml'],
        output='screen'
    )

    lifecycle_map = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_map_server',
        output='screen',
        parameters=[{
            'autostart': True,
            'node_names': ['map_server']
        }]
    )

    lifecycle_amcl = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_amcl',
        output='screen',
        parameters=[{
            'autostart': True,
            'node_names': ['amcl']
        }]
    )

    return LaunchDescription([
        map_server,
        RegisterEventHandler(OnProcessStart(target_action=map_server, on_start=[TimerAction(period=3.0, actions=[lifecycle_map])])),
        amcl,
        RegisterEventHandler(OnProcessStart(target_action=amcl, on_start=[TimerAction(period=3.0, actions=[lifecycle_amcl])]))
    ])
