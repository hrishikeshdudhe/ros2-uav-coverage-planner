#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geographic_msgs.msg import GeoPointStamped

from tf2_ros import TransformBroadcaster
from geometry_msgs.msg import TransformStamped


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

        # TF broadcaster
        self.tf_broadcaster = TransformBroadcaster(self)

        self.get_logger().info('Waiting for gp_origin to define map origin...')

        # Store reference GPS (optional future ENU use)
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

        self.ref_lat = lat
        self.ref_lon = lon
        self.ref_alt = alt

        t = TransformStamped()

        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = "map"
        t.child_frame_id = "gps"

        # Identity transform (define gps as origin of map frame)
        t.transform.translation.x = 0.0
        t.transform.translation.y = 0.0
        t.transform.translation.z = 0.0

        t.transform.rotation.x = 0.0
        t.transform.rotation.y = 0.0
        t.transform.rotation.z = 0.0
        t.transform.rotation.w = 1.0

        self.tf_broadcaster.sendTransform(t)

        self.anchor_set = True

        self.get_logger().info(
            'Map origin defined.\n'
            'TF published: map → gps\n'
            'RViz Satellite can now correctly align tiles.'
        )


def main():
    rclpy.init()
    node = MapAnchor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()