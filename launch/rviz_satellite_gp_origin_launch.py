"""from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    # Fake gp_origin node
    fake_gp_origin_node = Node(
        package='gps_anchor',
        executable='fake_gp_origin',  # you need to save the Python file as fake_gp_origin.py
        name='fake_gp_origin',
        output='screen'
    )

    # Map anchor node
    # - Subscribes to /tarot650/global_position/gp_origin
    # - Publishes earth -> map transform
    map_anchor_node = Node(
        package='gps_anchor',
        executable='map_anchor',
        name='map_anchor',
        output='screen',
        parameters=[{
            # Namespace + topic name are parameters so this
            # launch file stays flexible and comparable
            'gp_origin_topic': '/tarot650/global_position/gp_origin',
            'map_frame': 'map',
            'earth_frame': 'earth'
        }]
    )

    # RViz node (unchanged)
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', '/home/hrishi/thesis_ws/src/gps_anchor/rviz/rviz_satellite_config.rviz']
    )

    # Polygon node
    # - No latitude/longitude parameters anymore
    # - Works purely in map frame
    polygon_node = Node(
        package='gps_anchor',
        executable='gps_polygon_collector',
        name='gps_polygon_collector',
        output='screen'
    )

    return LaunchDescription([
        map_anchor_node,
        rviz_node,
        polygon_node,
        fake_gp_origin_node
    ])

"""

from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
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
            arguments=['-d', '/home/hrishi/thesis_ws/src/gps_anchor/rviz/rviz_satellite_config.rviz']
        )
    ])
