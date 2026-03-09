#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from geometry_msgs.msg import Point32, PolygonStamped
from opennav_coverage_msgs.action import ComputeCoveragePath
from opennav_coverage_msgs.msg import Coordinate

class CoverageClient(Node):
    def __init__(self):
        super().__init__('coverage_client')

        # --------------------------------------------------
        # Subscribe to polygon collected
        # --------------------------------------------------
        self.polygon_sub = self.create_subscription(
            PolygonStamped,
            '/robot_namespace/collected_polygon',
            self.polygon_callback,
            10
        )

        # --------------------------------------------------
        # Action Client
        # --------------------------------------------------
        self._action_client = ActionClient(
            self,
            ComputeCoveragePath,
            '/coverage_server/compute_coverage_path'
        )

        self.get_logger().info("Coverage Client Ready.")

    # --------------------------------------------------
    # Polygon callback
    # --------------------------------------------------
    def polygon_callback(self, msg: PolygonStamped):
        if len(msg.polygon.points) < 3:
            self.get_logger().warn("Polygon has less than 3 points. Ignoring.")
            return

        self.get_logger().info(f"Received polygon with {len(msg.polygon.points)} points.")

        # Transform PolygonStamped to list of Coordinates
        coordinates = []
        for p in msg.polygon.points:
            coord = Coordinate()
            coord.x = float(p.x)
            coord.y = float(p.y)
            coord.z = float(p.z)
            coordinates.append(coord)

        # Create action goal
        goal_msg = ComputeCoveragePath.Goal()
        goal_msg.polygon.coordinates = coordinates
        goal_msg.swath_width = 2.0  # example; adjust as needed

        # Send goal
        self.send_goal(goal_msg)

    # --------------------------------------------------
    # Send action goal
    # --------------------------------------------------
    def send_goal(self, goal_msg):
        self.get_logger().info("Waiting for action server...")
        self._action_client.wait_for_server()

        self.get_logger().info("Sending goal to coverage server...")
        send_goal_future = self._action_client.send_goal_async(goal_msg)
        send_goal_future.add_done_callback(self.goal_response_callback)

    # --------------------------------------------------
    # Goal response callback
    # --------------------------------------------------
    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().warn("Goal rejected by server.")
            return

        self.get_logger().info("Goal accepted. Waiting for result...")
        get_result_future = goal_handle.get_result_async()
        get_result_future.add_done_callback(self.get_result_callback)

    # --------------------------------------------------
    # Result callback
    # --------------------------------------------------
    def get_result_callback(self, future):
        result = future.result().result
        self.get_logger().info(f"Coverage path received: {len(result.path.poses)} poses.")


def main(args=None):
    rclpy.init(args=args)
    node = CoverageClient()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()