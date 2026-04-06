#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from nav_msgs.msg import Path
from geometry_msgs.msg import PolygonStamped
from std_srvs.srv import Trigger

from opennav_coverage_msgs.action import ComputeCoveragePath
from opennav_coverage_msgs.msg import Coordinate, Coordinates


class CoverageClient(Node):
    def __init__(self):
        super().__init__('coverage_client')

        self.latest_polygon = None

        # Subscriber
        self.polygon_sub = self.create_subscription(
            PolygonStamped,
            'collected_polygon',
            self.polygon_callback,
            10
        )

        # Publisher for the final navigation path (nav_msgs/Path)
        self.path_pub = self.create_publisher(
            Path,
            'coverage_path',
            10
        )

        # Publisher for debug components (optional)
        self.components_pub = self.create_publisher(
            Path,
            'coverage_turns_debug',
            10
        )

        # Action client
        self._action_client = ActionClient(
            self,
            ComputeCoveragePath,
            '/robot_namespace/compute_coverage_path'
        )

        # Manual trigger service
        self.trigger_srv = self.create_service(
            Trigger,
            'start_coverage',
            self.start_coverage_callback
        )

        self.get_logger().info("Coverage Client Ready. Waiting for polygon + trigger...")

    def polygon_callback(self, msg: PolygonStamped):
        self.latest_polygon = msg
        self.get_logger().info(
            f"Polygon received with {len(msg.polygon.points)} points. "
            "Call /start_coverage to begin planning."
        )

    def start_coverage_callback(self, request, response):
        if self.latest_polygon is None:
            response.success = False
            response.message = "No polygon available."
            self.get_logger().warn("No polygon available to send.")
            return response

        if len(self.latest_polygon.polygon.points) < 3:
            response.success = False
            response.message = "Polygon has less than 3 points."
            self.get_logger().warn("Polygon invalid.")
            return response

        self.get_logger().info("Starting coverage planning...")

        # Convert Polygon → Coordinates
        coordinates = []
        for p in self.latest_polygon.polygon.points:
            coord = Coordinate()
            coord.axis1 = float(p.x)
            coord.axis2 = float(p.y)
            coordinates.append(coord)

        # Create goal message
        goal_msg = ComputeCoveragePath.Goal()
        polygon_msg = Coordinates()
        polygon_msg.coordinates = coordinates
        goal_msg.polygons = [polygon_msg]
        goal_msg.frame_id = "map"

        # Wait for server
        self.get_logger().info("Waiting for coverage server...")
        if not self._action_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error("Coverage server not available!")
            response.success = False
            response.message = "Coverage server not available."
            return response

        # Send goal
        self.get_logger().info("Coverage server ready. Sending goal...")
        send_goal_future = self._action_client.send_goal_async(goal_msg)
        send_goal_future.add_done_callback(self.goal_response_callback)

        response.success = True
        response.message = "Coverage request sent."
        return response

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().warn("Goal rejected.")
            return

        self.get_logger().info("Goal accepted. Waiting for result...")
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        result_msg = future.result().result

        # Log error code + planning time
        self.get_logger().info(
            f"Coverage planning finished. Error code: {result_msg.error_code}"
        )
        self.get_logger().info(
            f"Planning time: {result_msg.planning_time.sec}.{result_msg.planning_time.nanosec}s"
        )

        nav_path = result_msg.nav_path
        self.get_logger().info(
            f"Final navigation path received with {len(nav_path.poses)} poses."
        )

        # Publish the final path
        self.path_pub.publish(nav_path)

        components = result_msg.coverage_path

        self.get_logger().info(
            f"coverage_path: {len(components.swaths)} swaths, "
            f"{len(components.turns)} turn segments."
        )

        # Log swath endpoints
        for i, sw in enumerate(components.swaths):
            self.get_logger().info(
                f"Swath {i}: start=({sw.start.x}, {sw.start.y}), "
                f"end=({sw.end.x}, {sw.end.y})"
            )

        # Debug publish each turn segment (optional)
        for i, turn in enumerate(components.turns):
            self.get_logger().info(f"Turn {i}: {len(turn.poses)} poses")
            turn.header.frame_id = "map"
            self.components_pub.publish(turn)


def main(args=None):
    rclpy.init(args=args)
    node = CoverageClient()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()