from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # -------------------------------
    # Coverage Server (Lifecycle Node)
    # -------------------------------
    coverage_server_node = Node(
        package='opennav_coverage',
        executable='opennav_coverage',
        name='coverage_server',
        namespace='robot_namespace',
        output='screen'
    )

    # -------------------------------
    # Coverage Client
    # -------------------------------
    coverage_client_node = Node(
        package='gps_anchor',
        executable='coverage_client',
        name='coverage_client',
        namespace='robot_namespace',
        output='screen'
    )

    # -------------------------------
    # Lifecycle Manager (auto-activate server)
    # -------------------------------
    lifecycle_manager_node = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_coverage',
        namespace='robot_namespace',
        parameters=[{
            # Full namespaced node
            'node_names': ['coverage_server'],  
            'autostart': True
        }],
        output='screen'
    )

    return LaunchDescription([
        coverage_server_node,
        coverage_client_node,
        lifecycle_manager_node
    ])