#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geographic_msgs.msg import GeoPointStamped

class FakeGpOrigin(Node):
    def __init__(self):
        super().__init__('fake_gp_origin')
        self.pub = self.create_publisher(GeoPointStamped, '/tarot650/global_position/gp_origin', 10)
        self.timer = self.create_timer(1.0, self.publish_origin)

    def publish_origin(self):
        msg = GeoPointStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'earth'
        msg.position.latitude = 49.4255
        msg.position.longitude = 7.755
        msg.position.altitude = 271.0
        self.pub.publish(msg)
        self.get_logger().info('Published fake gp_origin')
 
def main():
    rclpy.init()
    node = FakeGpOrigin()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
