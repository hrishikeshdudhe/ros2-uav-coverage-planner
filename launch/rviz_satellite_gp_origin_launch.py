from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    # Resolve RViz config path relative to gps_anchor package
    rviz_config = os.path.join(
        get_package_share_directory('gps_anchor'),
        'rviz',
        'rviz_satellite_config.rviz'
    )

    return LaunchDescription([
        # Fake GP origin
        Node(
            package='gps_anchor',
            executable='fake_gp_origin',
            name='fake_gp_origin',
            output='screen'
        ),

        # Map anchor: sets map frame at gp_origin
        Node(
            package='gps_anchor',
            executable='map_anchor',
            name='map_anchor',
            output='screen'
        ),

        # GPS publisher: publishes /gps/fix at gp_origin
        Node(
            package='gps_anchor',
            executable='fixed_gps_publisher',
            name='fixed_gps_publisher',
            output='screen'
        ),

        # Polygon collector
        Node(
            package='gps_anchor',
            executable='gps_polygon_collector',
            name='gps_polygon_collector',
            output='screen'
        ),

        # RViz
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_config]
        )
    ])
