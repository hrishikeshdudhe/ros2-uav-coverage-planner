#!/usr/bin/env python3

import math
import rclpy
from rclpy.node import Node

from geometry_msgs.msg import PointStamped, PolygonStamped, Point32
from visualization_msgs.msg import Marker
from std_srvs.srv import Trigger
from std_msgs.msg import Empty

CLOSE_RADIUS = 3.0

def distance_2d(p1, p2):
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)


class PolygonCollector(Node):

    def __init__(self):
        super().__init__('polygon_collector')

        self.points = []
        self.polygon_closed = False

        self.create_subscription(
            PointStamped,
            'clicked_point',
            self.point_callback,
            10
        )

        self.polygon_pub = self.create_publisher(
            PolygonStamped,
            'collected_polygon',
            10
        )

        self.marker_pub = self.create_publisher(
            Marker,
            'polygon_marker',
            10
        )

        # Trigger
        self.trigger_pub = self.create_publisher(
            Empty,
            'polygon_ready',
            10
        )

        # Reset topic
        self.create_subscription(
            Empty,
            'coverage_reset',
            self.reset_callback,
            10
        )

        self.get_logger().info("Polygon Collector Ready")

    # Reset
    def reset_callback(self, _):
        self.points = []
        self.polygon_closed = False
        marker = Marker()
        marker.header.frame_id = "map"
        marker.action = Marker.DELETEALL
        self.marker_pub.publish(marker)
        self.polygon_pub.publish(PolygonStamped())
        self.get_logger().info("Polygon reset")

    # Input
    def point_callback(self, msg: PointStamped):

        if self.polygon_closed:
            return
        p = msg.point
        # check closing condition
        if len(self.points) >= 3:
            if distance_2d(p, self.points[0]) <= CLOSE_RADIUS:
                self.get_logger().info("Polygon closed")
                self.polygon_closed = True
                self.points.append(self.points[0])  # close loop
                self.publish_polygon()
                self.publish_marker()
                # Trigger
                self.trigger_pub.publish(Empty())
                self.get_logger().info("Triggered planners")
                return

        self.points.append(p)
        self.publish_marker()

    # Publish polygon
    def publish_polygon(self):
        msg = PolygonStamped()
        msg.header.frame_id = "map"
        msg.header.stamp = self.get_clock().now().to_msg()
        for p in self.points:
            msg.polygon.points.append(
                Point32(x=p.x, y=p.y, z=p.z)
            )
        self.polygon_pub.publish(msg)

    # Rviz Marker
    def publish_marker(self):
        marker = Marker()
        marker.header.frame_id = "map"
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = "polygon"
        marker.id = 0
        marker.type = Marker.LINE_STRIP
        marker.action = Marker.ADD
        marker.scale.x = 0.5
        marker.color.a = 1.0
        if self.polygon_closed:
            marker.color.g = 1.0  # green = closed
        else:
            marker.color.r = 1.0  # red = open
        for p in self.points:
            marker.points.append(p)
        self.marker_pub.publish(marker)

def main():
    rclpy.init()
    node = PolygonCollector()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()