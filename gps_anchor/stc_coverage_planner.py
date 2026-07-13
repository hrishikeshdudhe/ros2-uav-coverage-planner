#!/usr/bin/env python3
import sys
sys.setrecursionlimit(100000)

import math
import rclpy
from rclpy.node import Node

from geometry_msgs.msg import PolygonStamped, PoseStamped
from nav_msgs.msg import Path
from std_msgs.msg import Empty
from visualization_msgs.msg import Marker


class STCCoveragePlanner(Node):

    def __init__(self):
        super().__init__('stc_coverage_planner')

        self.declare_parameter('resolution', 3.0)
        self.res = self.get_parameter('resolution').value

        self.poly = None
        self.running = False

        self.create_subscription(PolygonStamped, 'collected_polygon', self.cb_poly, 10)
        self.create_subscription(Empty, 'polygon_ready', self.cb_trigger, 10)
        self.create_subscription(Empty, 'coverage_reset', self.cb_reset, 10)

        self.pub_path = self.create_publisher(Path, 'coverage_path_stc', 10)
        self.pub_marker = self.create_publisher(Marker, 'coverage_markers_stc', 10)

        self.get_logger().info("STC planner ready")

    def cb_poly(self, msg):
        self.poly = msg

    def cb_trigger(self, _):
        if self.running or self.poly is None:
            return
        self.running = True
        path = self.stc(self.poly)
        self.pub_path.publish(path)
        self.publish_markers(path)
        self.running = False

    def cb_reset(self, _):
        self.poly = None
        self.running = False
        empty = Path()
        empty.header.frame_id = "map"
        empty.header.stamp = self.get_clock().now().to_msg()
        self.pub_path.publish(empty)
        delete = Marker()
        delete.header.frame_id = "map"
        delete.ns = "stc"
        delete.action = Marker.DELETEALL
        self.pub_marker.publish(delete)
        self.get_logger().info("STC reset complete")

    def stc(self, poly_msg):
        poly = poly_msg.polygon.points
        if len(poly) < 3:
            return Path()
        xs = [p.x for p in poly]
        ys = [p.y for p in poly]
        xmin, xmax = min(xs), max(xs)
        ymin, ymax = min(ys), max(ys)
        step = self.res
        coords = {}
        cells = []
        r = 0
        y = ymin
        while y <= ymax:
            c = 0
            x = xmin
            while x <= xmax:
                if self.in_poly(x, y, poly):
                    cells.append((r, c))
                coords[(r, c)] = (x, y)
                x += step
                c += 1
            y += step
            r += 1
        if not cells:
            return Path()
        
        cell_set = set(cells)
        tree = {}
        def nbrs(cell):
            r, c = cell
            for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
                n = (r + dr, c + dc)
                if n in cell_set:
                    yield n

        visited = set()
        def build_tree(u):
            visited.add(u)
            tree[u] = []
            for v in nbrs(u):
                if v not in visited:
                    tree[u].append(v)
                    build_tree(v)

        root = cells[0]
        build_tree(root)
        order = []

        def traverse(u):
            order.append(coords[u])
            for v in tree.get(u, []):
                traverse(v)
                order.append(coords[u])  # backtrack

        traverse(root)
        path = Path()
        path.header.frame_id = "map"
        path.header.stamp = self.get_clock().now().to_msg()
        last_yaw = 0.0
        for i in range(len(order)):
            x, y = order[i]
            pose = PoseStamped()
            pose.header.frame_id = "map"
            pose.pose.position.x = float(x)
            pose.pose.position.y = float(y)
            if i < len(order) - 1:
                nx, ny = order[i + 1]
                yaw = math.atan2(ny - y, nx - x)
                last_yaw = yaw
            else:
                yaw = last_yaw
            pose.pose.orientation.x = 0.0
            pose.pose.orientation.y = 0.0
            pose.pose.orientation.z = math.sin(yaw / 2.0)
            pose.pose.orientation.w = math.cos(yaw / 2.0)
            path.poses.append(pose)
        return path

    def in_poly(self, x, y, poly):
        inside = False
        j = len(poly) - 1
        for i in range(len(poly)):
            xi, yi = poly[i].x, poly[i].y
            xj, yj = poly[j].x, poly[j].y
            if (yi > y) != (yj > y):
                xin = (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi
                if x < xin:
                    inside = not inside
            j = i
        return inside

    def publish_markers(self, path):
        if not path.poses:
            return
        start = path.poses[0].pose.position
        end = path.poses[-1].pose.position
        m1 = Marker()
        m1.header.frame_id = "map"
        m1.ns = "stc"
        m1.id = 0
        m1.type = Marker.SPHERE
        m1.pose.position = start
        m1.scale.x = m1.scale.y = m1.scale.z = 2.0
        m1.color.a = 1.0
        m1.color.g = 1.0

        m2 = Marker()
        m2.header.frame_id = "map"
        m2.ns = "stc"
        m2.id = 1
        m2.type = Marker.SPHERE
        m2.pose.position = end
        m2.scale.x = m2.scale.y = m2.scale.z = 2.0
        m2.color.a = 1.0
        m2.color.r = 1.0

        self.pub_marker.publish(m1)
        self.pub_marker.publish(m2)

def main():
    rclpy.init()
    node = STCCoveragePlanner()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()