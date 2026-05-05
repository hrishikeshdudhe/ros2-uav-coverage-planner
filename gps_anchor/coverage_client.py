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
        self.coverage_started = False

        # Subscribers
        self.create_subscription(
            PolygonStamped,
            'collected_polygon',
            self.polygon_callback,
            10
        )

        self.create_subscription(
            Empty,
            'polygon_reset',
            self.reset_callback,
            10
        )

        # Publisher
        self.path_pub = self.create_publisher(
            Path,
            'coverage_path',
            10
        )

        # Action client
        self.client = ActionClient(
            self,
            ComputeCoveragePath,
            '/robot_namespace/compute_coverage_path'
        )

        self.marker_pub = self.create_publisher(
            Marker,
            'coverage_markers',
            10
        )

    def is_closed(self, msg):
        if len(msg.polygon.points) < 4:
            return False

        a = msg.polygon.points[0]
        b = msg.polygon.points[-1]

        return abs(a.x - b.x) < 0.01 and abs(a.y - b.y) < 0.01

    def publish_start_end_markers(self, path):
        if len(path.poses) == 0:
            return

        # -------- START MARKER (GREEN) --------
        start = path.poses[0].pose.position

        start_marker = Marker()
        start_marker.header.frame_id = "map"
        start_marker.header.stamp = self.get_clock().now().to_msg()
        start_marker.ns = "coverage_points"
        start_marker.id = 0
        start_marker.type = Marker.SPHERE
        start_marker.action = Marker.ADD

        start_marker.pose.position = start
        start_marker.scale.x = 1.5
        start_marker.scale.y = 1.5
        start_marker.scale.z = 1.5

        start_marker.color.a = 1.0
        start_marker.color.r = 0.0
        start_marker.color.g = 1.0
        start_marker.color.b = 0.0

        # -------- END MARKER (RED) --------
        end = path.poses[-1].pose.position

        end_marker = Marker()
        end_marker.header.frame_id = "map"
        end_marker.header.stamp = self.get_clock().now().to_msg()
        end_marker.ns = "coverage_points"
        end_marker.id = 1
        end_marker.type = Marker.SPHERE
        end_marker.action = Marker.ADD

        end_marker.pose.position = end
        end_marker.scale.x = 1.5
        end_marker.scale.y = 1.5
        end_marker.scale.z = 1.5

        end_marker.color.a = 1.0
        end_marker.color.r = 1.0
        end_marker.color.g = 0.0
        end_marker.color.b = 0.0

        # Publish both
        self.marker_pub.publish(start_marker)
        self.marker_pub.publish(end_marker)

    def polygon_callback(self, msg):
        self.latest_polygon = msg

        if self.is_closed(msg) and not self.coverage_started:
            self.coverage_started = True
            self.start_coverage()

    def reset_callback(self, _):
        self.coverage_started = False
        self.latest_polygon = None

        delete_marker = Marker()
        delete_marker.header.frame_id = "map"
        delete_marker.ns = "coverage_points"
        delete_marker.action = Marker.DELETEALL
        self.marker_pub.publish(delete_marker)

        empty_path = Path()
        empty_path.header.frame_id = "map"
        empty_path.header.stamp = self.get_clock().now().to_msg()
        self.path_pub.publish(empty_path)

    def start_coverage(self):
        if self.latest_polygon is None:
            return

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
            return

        future = self.client.send_goal_async(goal)
        future.add_done_callback(self.goal_response)

    def goal_response(self, future):
        handle = future.result()
        if not handle.accepted:
            return

        result_future = handle.get_result_async()
        result_future.add_done_callback(self.result_callback)

    def result_callback(self, future):
        result = future.result().result
        self.path_pub.publish(result.nav_path)
        self.publish_start_end_markers(result.nav_path)


def main():
    rclpy.init()
    node = CoverageClient()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()