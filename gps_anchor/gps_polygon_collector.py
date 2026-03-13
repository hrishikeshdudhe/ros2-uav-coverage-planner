#!/usr/bin/env python3

import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PointStamped, PolygonStamped, Point32
from visualization_msgs.msg import Marker
from std_srvs.srv import Trigger

CLOSE_RADIUS = 3.0  # meters

def distance_2d(p1, p2):
    """Compute 2D Euclidean distance between points."""
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)


class PolygonCollector(Node):
    def __init__(self):
        super().__init__('polygon_collector')

        from rclpy.qos import QoSProfile, QoSDurabilityPolicy

        # Create QoS profile for transient local durability
        transient_qos = QoSProfile(depth=1, durability=QoSDurabilityPolicy.TRANSIENT_LOCAL)

        # Storage
        self.points = []
        self.polygon_closed = False

        # Subscribers
        self.point_sub = self.create_subscription(
            PointStamped,
            'clicked_point',
            self.point_callback,
            10
        )

        # Publishers
        self.polygon_pub = self.create_publisher(
            PolygonStamped,
            'collected_polygon',
            transient_qos
        )

        self.marker_pub = self.create_publisher(
            Marker,
            'polygon_marker',
            transient_qos  
        )

        # Reset Service
        self.reset_srv = self.create_service(
            Trigger,
            'reset_polygon',
            self.reset_callback
        )

        self.get_logger().info("Polygon Collector Ready.")

    # Reset Service
    def reset_callback(self, request, response):
        
        self.points = []
        self.polygon_closed = False
        
        marker = Marker()
        marker.header.frame_id = "map"
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = "polygon"
        marker.id = 0
        marker.action = Marker.DELETE

        self.marker_pub.publish(marker)

        response.success = True
        response.message = "Polygon reset."

        self.get_logger().info("Polygon reset. Ready to collect new points.")

        return response

    # Clicked Point Callback
    def point_callback(self, msg: PointStamped):

        if self.polygon_closed:
            self.get_logger().info("Polygon already closed. Reset to start a new one.")
            return

        # Directly use the clicked point in map frame
        new_point = msg.point

        # Check closing condition
        if len(self.points) >= 3:
            first_point = self.points[0]
            dist = distance_2d(new_point, first_point)
            if dist <= CLOSE_RADIUS:
                self.get_logger().info("Closing polygon.")
                self.polygon_closed = True
                self.publish_polygon(close=True)
                self.publish_marker(close=True)
                return

        # Otherwise add point
        self.points.append(new_point)
        self.get_logger().info(f"Added point ({new_point.x:.2f}, {new_point.y:.2f})")

        self.publish_polygon(close=False)
        self.publish_marker(close=False)

    # Publish Polygon
    def publish_polygon(self, close=False):
        poly_msg = PolygonStamped()
        poly_msg.header.frame_id = "map"
        poly_msg.header.stamp = self.get_clock().now().to_msg()

        for p in self.points:
            poly_msg.polygon.points.append(Point32(x=p.x, y=p.y, z=p.z))

        if close and len(self.points) >= 3:
            first = self.points[0]
            poly_msg.polygon.points.append(Point32(x=first.x, y=first.y, z=first.z))

        self.polygon_pub.publish(poly_msg)

    # Publish Marker
    def publish_marker(self, close=False):
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
            marker.scale.x = 1.0 
            marker.scale.y = 1.0 
            marker.scale.z = 1.0
            marker.color.r = 0.0
            marker.color.g = 1.0
            marker.color.b = 0.0
        else:
            marker.scale.x = 1.0 
            marker.scale.y = 1.0 
            marker.scale.z = 1.0
            marker.color.r = 1.0
            marker.color.g = 0.0
            marker.color.b = 0.0

        for p in self.points:
            marker.points.append(p)

        if close and len(self.points) >= 3:
            marker.points.append(self.points[0])

        self.marker_pub.publish(marker)

# Main
def main(args=None):
    rclpy.init(args=args)
    node = PolygonCollector()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
