#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from nav_msgs.msg import Path
from geometry_msgs.msg import PolygonStamped
from std_msgs.msg import Empty
from visualization_msgs.msg import Marker

from opennav_coverage_msgs.action import ComputeCoveragePath
from opennav_coverage_msgs.msg import Coordinate, Coordinates


class CoverageClient(Node):

    def __init__(self):
        super().__init__('coverage_client')

        self.latest_polygon = None
        self.running = False

        # SUBSCRIBERS
        self.create_subscription(
            PolygonStamped,
            'collected_polygon',
            self.polygon_callback,
            10
        )

        self.create_subscription(
            Empty,
            'polygon_ready',
            self.trigger_callback,
            10
        )

        self.create_subscription(
            Empty,
            'coverage_reset',
            self.reset_callback,
            10
        )

        # Action client
        self.client = ActionClient(
            self,
            ComputeCoveragePath,
            'compute_coverage_path'
        )

        # Outputs
        self.path_pub = self.create_publisher(
            Path,
            'coverage_path_opennav',
            10
        )

        self.marker_pub = self.create_publisher(
            Marker,
            'coverage_markers_opennav',
            10
        )

    # Store Polygon
    def polygon_callback(self, msg):
        self.latest_polygon = msg

    # Trigger
    def trigger_callback(self, _):

        if self.running:
            return

        if self.latest_polygon is None:
            self.get_logger().warn("No polygon received")
            return

        if len(self.latest_polygon.polygon.points) < 3:
            self.get_logger().warn("Invalid polygon")
            return

        self.running = True
        self.start_coverage()

    # Reset
    def reset_callback(self, _):
        self.latest_polygon = None
        self.running = False

        empty = Path()
        empty.header.frame_id = "map"
        self.path_pub.publish(empty)

        delete = Marker()
        delete.action = Marker.DELETEALL
        self.marker_pub.publish(delete)
        self.get_logger().info("OpenNav reset via shared topic")

    # Start Coverage
    def start_coverage(self):

        coords = []

        for p in self.latest_polygon.polygon.points:
            c = Coordinate()
            c.axis1 = float(p.x)
            c.axis2 = float(p.y)
            coords.append(c)

        goal = ComputeCoveragePath.Goal()
        poly = Coordinates()
        poly.coordinates = coords

        goal.polygons = [poly]
        goal.frame_id = "map"

        if not self.client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error("Coverage server not available")
            return

        self.get_logger().info("Sending OpenNav coverage goal")

        future = self.client.send_goal_async(goal)
        future.add_done_callback(self.goal_response)

    # Callbacks
    def goal_response(self, future):
        handle = future.result()

        if not handle.accepted:
            self.running = False
            return

        result_future = handle.get_result_async()
        result_future.add_done_callback(self.result_callback)

    def result_callback(self, future):

        self.running = False

        result = future.result().result

        path = result.nav_path
        self.path_pub.publish(path)

        self.publish_markers(path)

    # Markers
    def publish_markers(self, path):

        if len(path.poses) == 0:
            return

        start = path.poses[0].pose.position
        end = path.poses[-1].pose.position

        # Start
        m1 = Marker()
        m1.header.frame_id = "map"
        m1.ns = "opennav_points"
        m1.id = 0
        m1.type = Marker.SPHERE
        m1.action = Marker.ADD
        m1.pose.position = start
        m1.scale.x = m1.scale.y = m1.scale.z = 1.5
        m1.color.a = 1.0
        m1.color.g = 1.0

        # End
        m2 = Marker()
        m2.header.frame_id = "map"
        m2.ns = "opennav_points"
        m2.id = 1
        m2.type = Marker.SPHERE
        m2.action = Marker.ADD
        m2.pose.position = end
        m2.scale.x = m2.scale.y = m2.scale.z = 1.5
        m2.color.a = 1.0
        m2.color.r = 1.0

        self.marker_pub.publish(m1)
        self.marker_pub.publish(m2)


def main():
    rclpy.init()
    node = CoverageClient()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()