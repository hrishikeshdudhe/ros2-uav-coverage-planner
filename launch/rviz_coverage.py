from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():

    # Coverage Server Node
    coverage_server_node = Node(
        package='opennav_coverage',
        executable='opennav_coverage',   
        name='coverage_server',
        output='screen'
    )

    # Coverage Client Node
    coverage_client_node = Node(
        package='gps_anchor',
        executable='coverage_client',
        name='coverage_client',
        output='screen'
    )


    return LaunchDescription([
        coverage_server_node,
        coverage_client_node,
    ])