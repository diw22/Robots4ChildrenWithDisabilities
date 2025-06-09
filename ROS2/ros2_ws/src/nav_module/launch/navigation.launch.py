from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    config_dir = 'config/'  # relative path to the config directory

    return LaunchDescription([

        # Map server is only needed if using a static map (i.e. not using SLAM)
        # Node(
        #     package='nav2_map_server',
        #     executable='map_server',
        #     name='map_server',
        #     parameters=[config_dir + 'map.yaml'],
        #     output='screen'
        # ),

        # AMCL for localization using laser scans
        Node(
            package='nav2_amcl',
            executable='amcl',
            name='amcl',
            parameters=[config_dir + 'amcl.yaml'],
            output='screen'
        ),

        # Global planner for path generation
        Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            parameters=[
                config_dir + 'move_base.yaml',
                config_dir + 'global_costmap.yaml',
                config_dir + 'costmap_common.yaml'
            ],
            output='screen'
        ),

        # Local controller for path following and obstacle avoidance
        Node(
            package='nav2_controller',
            executable='controller_server',
            name='controller_server',
            parameters=[
                config_dir + 'move_base.yaml',
                config_dir + 'local_costmap.yaml',
                config_dir + 'costmap_common.yaml'
            ],
            output='screen'
        ),

        # Behavior Tree navigator for high-level goal handling
        Node(
            package='nav2_bt_navigator',
            executable='bt_navigator',
            name='bt_navigator',
            parameters=[config_dir + 'move_base.yaml'],
            output='screen'
        ),

        # Recovery behaviors (e.g. spin, backup, clear costmap)
        Node(
            package='nav2_recoveries',
            executable='recoveries_server',
            name='recoveries_server',
            parameters=[config_dir + 'move_base.yaml'],
            output='screen'
        ),

        # Custom navigator node that sends navigation goals (optional)
        Node(
            package='nav_module',
            executable='navigator_node',
            name='navigator_node',
            output='screen'
        ),
    ])
