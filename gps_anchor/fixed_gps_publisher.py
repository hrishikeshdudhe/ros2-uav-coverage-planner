#!/usr/bin/env python3

from geographic_msgs.msg import GeoPointStamped
from sensor_msgs.msg import NavSatFix
import rclpy
from rclpy.node import Node


class FixedGPSPublisher(Node):
    def __init__(self):
        super().__init__('fixed_gps_publisher')

        # Subscribe to gp_origin
        self.subscription = self.create_subscription(
            GeoPointStamped,
            '/tarot650/global_position/gp_origin',
            self.gp_origin_callback,
            10
        )

        self.publisher_ = self.create_publisher(NavSatFix, '/gps/fix', 10)
        self.lat = 0.0
        self.lon = 0.0
        self.alt = 0.0
        self.timer = self.create_timer(1.0, self.publish_fix)

    def gp_origin_callback(self, msg: GeoPointStamped):
        self.lat = msg.position.latitude
        self.lon = msg.position.longitude
        self.alt = msg.position.altitude

    def publish_fix(self):
        msg = NavSatFix()
        msg.latitude = self.lat
        msg.longitude = self.lon
        msg.altitude = self.alt
        self.publisher_.publish(msg)


"""class FixedGPSPublisher(Node):

    def __init__(self):
        super().__init__('fixed_gps_publisher')

        # Declare parameters for runtime configuration
        self.declare_parameter('latitude', 49.4401)   # default Kaiserslautern
        self.declare_parameter('longitude', 7.7491)
        self.declare_parameter('altitude', 0.0)

        # Publisher for NavSatFix
        self.publisher_ = self.create_publisher(
            NavSatFix,
            '/gps/fix',
            10
        )

        # Timer to periodically publish
        self.timer = self.create_timer(1.0, self.publish_fix)

    def publish_fix(self):
        # Read parameters
        lat = self.get_parameter('latitude').get_parameter_value().double_value
        lon = self.get_parameter('longitude').get_parameter_value().double_value
        alt = self.get_parameter('altitude').get_parameter_value().double_value

        # Create GPS message
        msg = NavSatFix()
        msg.latitude = lat
        msg.longitude = lon
        msg.altitude = alt

        # Publish
        self.publisher_.publish(msg)"""

def main():
    rclpy.init()
    node = FixedGPSPublisher()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()

