from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():

    # --------------------------------------------------
    # Coverage Server Node
    # --------------------------------------------------
    coverage_server_node = Node(
        package='opennav_coverage',
        executable='opennav_coverage',   # make sure this is the exact executable
        name='coverage_server',
        output='screen'
    )

    # --------------------------------------------------
    # Coverage Client Node
    # --------------------------------------------------
    coverage_client_node = Node(
        package='gps_anchor',
        executable='coverage_client',
        name='coverage_client',
        output='screen'
    )

    # --------------------------------------------------
    # RViz Node (optional)
    # --------------------------------------------------
    # You can use your existing RViz config or a minimal config
    rviz_config_file = os.path.join(
        get_package_share_directory('gps_anchor'),
        'rviz',
        'rviz_satellite_config.rviz'
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_file],
        output='screen'
    )

    return LaunchDescription([
        coverage_server_node,
        coverage_client_node,
        rviz_node
    ])