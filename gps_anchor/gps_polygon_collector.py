#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import PointStamped, Point, PolygonStamped, Point32
from visualization_msgs.msg import Marker
from std_srvs.srv import Trigger

from math import cos, radians, pi, sqrt


class GPSPolygonCollector(Node):

    def __init__(self):
        super().__init__('gps_polygon_collector')

        # ---- Parameters ----
        self.declare_parameter('origin_latitude', 49.4401)
        self.declare_parameter('origin_longitude', 7.7491)

        self.origin_lat = self.get_parameter('origin_latitude').value
        self.origin_lon = self.get_parameter('origin_longitude').value

        self.R = 6371000.0
        self.min_dist = 5.0

        self.points_xy = []
        self.points_gps = []
        self.closed = False

        # ---- ROS Interfaces ----
        self.create_subscription(PointStamped, '/clicked_point', self.point_cb, 10)

        self.marker_pub = self.create_publisher(Marker, '/polygon_marker', 10)
        self.poly_pub = self.create_publisher(PolygonStamped, '/polygon_gps', 10)

        self.create_service(Trigger, '/close_polygon', self.close_cb)

        self.get_logger().info('GPS Polygon Collector running')

    # ------------------------------------------------------------------

    def distance(self, a: Point, b: Point):
        return sqrt((a.x - b.x)**2 + (a.y - b.y)**2)

    def xy_to_latlon(self, x, y):
        dlat = y / self.R * (180.0 / pi)
        dlon = x / (self.R * cos(radians(self.origin_lat))) * (180.0 / pi)
        return self.origin_lat + dlat, self.origin_lon + dlon

    # ------------------------------------------------------------------

    def point_cb(self, msg: PointStamped):
        if self.closed:
            return

        p = Point(x=msg.point.x, y=msg.point.y, z=0.0)

        if self.points_xy and self.distance(p, self.points_xy[-1]) < self.min_dist:
            self.get_logger().warn('Point too close — ignored')
            return

        lat, lon = self.xy_to_latlon(p.x, p.y)

        self.points_xy.append(p)
        self.points_gps.append((lat, lon))

        self.get_logger().info(f'Point {len(self.points_xy)}: lat={lat:.6f}, lon={lon:.6f}')

        self.publish_markers()

    # ------------------------------------------------------------------

    def close_cb(self, req, res):
        if len(self.points_xy) < 3:
            res.success = False
            res.message = 'Need at least 3 points'
            return res

        self.closed = True
        self.publish_markers(close_loop=True)
        self.publish_polygon()

        self.get_logger().info('Polygon closed')
        res.success = True
        res.message = 'Polygon closed'
        return res

    # ------------------------------------------------------------------

    def publish_markers(self, close_loop=False):
        now = self.get_clock().now().to_msg()

        # ---- Points ----
        pts = Marker()
        pts.header.frame_id = 'map'
        pts.header.stamp = now
        pts.ns = 'points'
        pts.id = 0
        pts.type = Marker.SPHERE_LIST
        pts.action = Marker.ADD
        pts.scale.x = 1.0
        pts.scale.y = 1.0
        pts.scale.z = 1.0
        pts.color.r = 1.0
        pts.color.g = 0.0
        pts.color.b = 0.0
        pts.color.a = 1.0
        pts.points = list(self.points_xy)

        self.marker_pub.publish(pts)

        # ---- Edges ----
        line = Marker()
        line.header.frame_id = 'map'
        line.header.stamp = now
        line.ns = 'edges'
        line.id = 1
        line.type = Marker.LINE_STRIP
        line.action = Marker.ADD
        line.scale.x = 0.5
        line.color.r = 1.0
        line.color.g = 0.0
        line.color.b = 0.0
        line.color.a = 1.0

        line.points = list(self.points_xy)

        if close_loop:
            line.points.append(self.points_xy[0])

        self.marker_pub.publish(line)

    # ------------------------------------------------------------------

    def publish_polygon(self):
        poly = PolygonStamped()
        poly.header.frame_id = 'gps'
        poly.header.stamp = self.get_clock().now().to_msg()

        for lat, lon in self.points_gps:
            poly.polygon.points.append(Point32(x=lon, y=lat, z=0.0))

        self.poly_pub.publish(poly)


def main(args=None):
    rclpy.init(args=args)
    node = GPSPolygonCollector()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
