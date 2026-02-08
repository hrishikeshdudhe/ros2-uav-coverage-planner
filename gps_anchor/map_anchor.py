#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geographic_msgs.msg import GeoPointStamped
from tf2_ros import StaticTransformBroadcaster
from geometry_msgs.msg import TransformStamped
import math

class MapAnchor(Node):
    def __init__(self):
        super().__init__('map_anchor')

        self.tf_broadcaster = StaticTransformBroadcaster(self)
        self.anchor_set = False

        # Subscribe to gp_origin topic
        self.subscription = self.create_subscription(
            GeoPointStamped,
            '/tarot650/global_position/gp_origin',
            self.gp_origin_callback,
            10
        )

        self.get_logger().info('Waiting for gp_origin to anchor map frame...')

        # Earth radius
        self.R = 6378137.0  # meters, WGS84

        # Reference latitude/longitude for ENU conversion
        self.ref_lat = None
        self.ref_lon = None
        self.ref_alt = None

    def gp_origin_callback(self, msg: GeoPointStamped):
        if self.anchor_set:
            return

        lat = msg.position.latitude
        lon = msg.position.longitude
        alt = msg.position.altitude

        self.get_logger().info(f'Received gp_origin: lat={lat}, lon={lon}, alt={alt}')

        # Store reference as origin for ENU conversion
        self.ref_lat = lat
        self.ref_lon = lon
        self.ref_alt = alt

        # Map origin in ENU: origin of map frame relative to earth
        x, y, z = 0.0, 0.0, 0.0  # map origin coincides with gp_origin

        # Create TransformStamped
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'earth'
        t.child_frame_id = 'map'
        t.transform.translation.x = x
        t.transform.translation.y = y
        t.transform.translation.z = z

        # No rotation
        t.transform.rotation.x = 0.0
        t.transform.rotation.y = 0.0
        t.transform.rotation.z = 0.0
        t.transform.rotation.w = 1.0

        # Send static transform
        self.tf_broadcaster.sendTransform(t)
        self.anchor_set = True

        self.get_logger().info('Map frame anchored at gp_origin.')

        # Optional: log ENU conversion example
        dx, dy = self.latlon_to_xy(lat, lon)
        self.get_logger().info(f'ENU coordinates of gp_origin: x={dx:.2f} m, y={dy:.2f} m')

    def latlon_to_xy(self, lat, lon):
        """Convert lat/lon to ENU meters relative to reference."""
        if self.ref_lat is None or self.ref_lon is None:
            return 0.0, 0.0

        d_lat = math.radians(lat - self.ref_lat)
        d_lon = math.radians(lon - self.ref_lon)
        x = self.R * d_lon * math.cos(math.radians(self.ref_lat))
        y = self.R * d_lat
        return x, y

def main():
    rclpy.init()
    node = MapAnchor()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
