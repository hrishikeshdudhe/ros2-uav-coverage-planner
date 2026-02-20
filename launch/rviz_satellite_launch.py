#!/usr/bin/env python3
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    # Declare launch arguments for runtime configuration
    lat_arg = DeclareLaunchArgument('latitude', default_value='49.4401')
    lon_arg = DeclareLaunchArgument('longitude', default_value='7.7491')
    alt_arg = DeclareLaunchArgument('altitude', default_value='0.0')

    # GPS publisher node
    gps_node = Node(
        package='gps_anchor',
        executable='fixed_gps_publisher',
        name='fixed_gps_publisher',
        output='screen',
        parameters=[{
            'latitude': LaunchConfiguration('latitude'),
            'longitude': LaunchConfiguration('longitude'),
            'altitude': LaunchConfiguration('altitude')
        }]
    )

    # RViz node
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', '/home/hrishi/thesis_ws/src/gps_anchor/rviz/rviz_satellite_config.rviz']
    )
    
    # Polygon node
    polygon_node = Node(
    	package='gps_anchor',
    	executable='gps_polygon_collector',
    	output='screen',
    	parameters=[{
    		'origin_latitude': LaunchConfiguration('latitude'),
    		'origin_longitude': LaunchConfiguration('longitude'),
    		'origin_altitude': LaunchConfiguration('altitude')
    		}]
    )

    return LaunchDescription([
        lat_arg,
        lon_arg,
        alt_arg,
        gps_node,
        rviz_node,
        polygon_node
    ])

