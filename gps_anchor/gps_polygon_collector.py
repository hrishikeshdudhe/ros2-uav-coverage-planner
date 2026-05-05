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
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)


class PolygonCollector(Node):
    def __init__(self):
        super().__init__('polygon_collector')

        self.points = []
        self.polygon_closed = False

        # Subscriber
        self.create_subscription(
            PointStamped,
            'clicked_point',
            self.point_callback,
            10
        )

        # Publishers
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

        self.reset_pub = self.create_publisher(
            Empty,
            'polygon_reset',
            10
        )

        # Service
        self.create_service(
            Trigger,
            'reset_polygon',
            self.reset_callback
        )

    def reset_callback(self, request, response):
        self.points = []
        self.polygon_closed = False

        marker = Marker()
        marker.header.frame_id = "map"
        marker.action = Marker.DELETE
        marker.id = 0
        marker.ns = "polygon"
        self.marker_pub.publish(marker)

        self.reset_pub.publish(Empty())

        response.success = True
        response.message = "Polygon reset"
        return response

    def point_callback(self, msg: PointStamped):
        if self.polygon_closed:
            return

        p = msg.point

        if len(self.points) >= 3:
            if distance_2d(p, self.points[0]) <= CLOSE_RADIUS:
                self.polygon_closed = True
                self.publish_polygon(close=True)
                self.publish_marker(close=True)
                return

        self.points.append(p)
        self.publish_polygon(close=False)
        self.publish_marker(close=False)

    def publish_polygon(self, close=False):
        msg = PolygonStamped()
        msg.header.frame_id = "map"

        for p in self.points:
            msg.polygon.points.append(Point32(x=p.x, y=p.y, z=p.z))

        if close:
            first = self.points[0]
            msg.polygon.points.append(Point32(x=first.x, y=first.y, z=first.z))

        self.polygon_pub.publish(msg)

    def publish_marker(self, close=False):
        marker = Marker()
        marker.header.frame_id = "map"
        marker.ns = "polygon"
        marker.id = 0
        marker.type = Marker.LINE_STRIP
        marker.action = Marker.ADD

        marker.scale.x = 1.0
        marker.color.a = 1.0

        if self.polygon_closed:
            marker.color.g = 1.0
        else:
            marker.color.r = 1.0

        for p in self.points:
            marker.points.append(p)

        if close:
            marker.points.append(self.points[0])

        self.marker_pub.publish(marker)


def main():
    rclpy.init()
    node = PolygonCollector()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()