#!/usr/bin/env python3

from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():

    namespace = 'robot_namespace'

    rviz_config = os.path.join(
        get_package_share_directory('gps_anchor'),
        'rviz',
        'rviz_satellite_config.rviz'
    )

    return LaunchDescription([

        # =====================================================
        # GPS + MAP SETUP
        # =====================================================
        Node(
            package='gps_anchor',
            executable='fake_gp_origin',
            name='fake_gp_origin',
            namespace=namespace,
            output='screen'
        ),

        Node(
            package='gps_anchor',
            executable='map_anchor',
            name='map_anchor',
            namespace=namespace,
            output='screen'
        ),

        Node(
            package='gps_anchor',
            executable='fixed_gps_publisher',
            name='fixed_gps_publisher',
            namespace=namespace,
            output='screen'
        ),

        # =====================================================
        # POLYGON COLLECTOR (single source of truth)
        # =====================================================
        Node(
            package='gps_anchor',
            executable='gps_polygon_collector',
            name='gps_polygon_collector',
            namespace=namespace,
            output='screen'
        ),

        # =====================================================
        # OPENNAV COVERAGE SYSTEM
        # =====================================================
        Node(
            package='opennav_coverage',
            executable='opennav_coverage',
            name='coverage_server',
            namespace=namespace,
            output='screen'
        ),

        Node(
            package='gps_anchor',
            executable='coverage_client',
            name='coverage_client',
            namespace=namespace,
            output='screen'
        ),

        # =====================================================
        # Custom COVERAGE PLANNER
        # =====================================================
        Node(
            package='gps_anchor',
            executable='stc_coverage_planner',
            name='stc_coverage_planner',
            namespace=namespace,
            output='screen'
        ),

        # =====================================================
        # LIFECYCLE MANAGER (OpenNav only)
        # =====================================================
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_coverage',
            namespace=namespace,
            parameters=[{
                'node_names': ['coverage_server'],
                'autostart': True
            }],
            output='screen'
        ),

        # =====================================================
        # RVIZ
        # =====================================================
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            namespace=namespace,
            arguments=['-d', rviz_config],
            remappings=[('/tf', 'tf')],
            output='screen'
        ),
    ])