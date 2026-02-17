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

        self.publisher_ = self.create_publisher(NavSatFix, 'gps/fix', 10)
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

def main():
    rclpy.init()
    node = FixedGPSPublisher()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()

