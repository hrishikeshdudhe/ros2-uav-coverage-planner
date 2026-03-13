#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geographic_msgs.msg import GeoPointStamped


class MapAnchor(Node):

    def __init__(self):
        super().__init__('map_anchor')

        self.anchor_set = False

        # Subscribe to gp_origin topic
        self.subscription = self.create_subscription(
            GeoPointStamped,
            '/tarot650/global_position/gp_origin',
            self.gp_origin_callback,
            10
        )

        self.get_logger().info('Waiting for gp_origin to define map origin...')

        # Earth radius (WGS84)
        self.R = 6378137.0  # meters

        # Reference latitude/longitude for optional ENU conversion
        self.ref_lat = None
        self.ref_lon = None
        self.ref_alt = None

    def gp_origin_callback(self, msg: GeoPointStamped):
        if self.anchor_set:
            return

        lat = msg.position.latitude
        lon = msg.position.longitude
        alt = msg.position.altitude

        self.get_logger().info(
            f'Received gp_origin:\n'
            f'  Latitude:  {lat}\n'
            f'  Longitude: {lon}\n'
            f'  Altitude:  {alt}'
        )

        # Store reference as logical origin of map frame
        self.ref_lat = lat
        self.ref_lon = lon
        self.ref_alt = alt

        self.anchor_set = True

        self.get_logger().info(
            'Map origin defined.\n'
            'map (0,0,0) now corresponds to this GPS location.'
        )

def main():
    rclpy.init()
    node = MapAnchor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()