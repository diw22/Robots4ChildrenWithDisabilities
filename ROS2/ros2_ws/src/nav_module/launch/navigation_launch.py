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

    planner = Node(
        package='nav2_planner',
        executable='planner_server',
        name='planner_server',
        parameters=[
            config_path + '/move_base.yaml',
            config_path + '/global_costmap.yaml',
            config_path + '/costmap_common.yaml'
        ],
        output='screen'
    )

    controller = Node(
        package='nav2_controller',
        executable='controller_server',
        name='controller_server',
        parameters=[
            config_path + '/move_base.yaml',
            config_path + '/local_costmap.yaml',
            config_path + '/costmap_common.yaml'
        ],
        output='screen'
    )

    bt = Node(
        package='nav2_bt_navigator',
        executable='bt_navigator',
        name='bt_navigator',
        parameters=[config_path + '/move_base.yaml'],
        output='screen'
    )

    lifecycle = lambda name: Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name=f'lifecycle_manager_{name}',
        output='screen',
        parameters=[{'autostart': True, 'node_names': [name]}]
    )

    return LaunchDescription([
        planner,
        RegisterEventHandler(OnProcessStart(planner, [TimerAction(period=3.0, actions=[lifecycle('planner_server')])])),
        controller,
        RegisterEventHandler(OnProcessStart(controller, [TimerAction(period=3.0, actions=[lifecycle('controller_server')])])),
        bt,
        RegisterEventHandler(OnProcessStart(bt, [TimerAction(period=3.0, actions=[lifecycle('bt_navigator')])]))
    ])
