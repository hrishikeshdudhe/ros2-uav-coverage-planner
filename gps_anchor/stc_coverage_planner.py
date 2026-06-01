#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import PolygonStamped, PoseStamped
from nav_msgs.msg import Path
from std_msgs.msg import Empty
from visualization_msgs.msg import Marker


class STCCoveragePlanner(Node):

    def __init__(self):
        super().__init__('stc_coverage_planner')

        self.declare_parameter('resolution', 5.0)
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

    # STC
    def stc(self, poly_msg):

        poly = poly_msg.polygon.points

        if len(poly) < 3:
            return Path()

        xs = [p.x for p in poly]
        ys = [p.y for p in poly]

        xmin, xmax = min(xs), max(xs)
        ymin, ymax = min(ys), max(ys)

        step = self.res

        cells = []
        coords = {}

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

        def nbrs(cell):
            r, c = cell
            for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
                n = (r+dr, c+dc)
                if n in cell_set:
                    yield n

        visited = set()
        order = []

        def dfs(u):
            visited.add(u)
            order.append(coords[u])

            for v in nbrs(u):
                if v not in visited:
                    dfs(v)
                    order.append(coords[u])  # STC backtrack

        start = cells[0]
        dfs(start)

        path = Path()
        path.header.frame_id = "map"
        path.header.stamp = self.get_clock().now().to_msg()

        for x, y in order:
            p = PoseStamped()
            p.header.frame_id = "map"
            p.pose.position.x = float(x)
            p.pose.position.y = float(y)
            p.pose.orientation.w = 1.0
            path.poses.append(p)

        return path

    # geometry
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

    # markers
    def publish_markers(self, path):

        if len(path.poses) == 0:
            return

        s = path.poses[0].pose.position
        e = path.poses[-1].pose.position

        m1 = Marker()
        m1.header.frame_id = "map"
        m1.ns = "stc"
        m1.id = 0
        m1.type = Marker.SPHERE
        m1.action = Marker.ADD
        m1.pose.position = s
        m1.scale.x = m1.scale.y = m1.scale.z = 2.0
        m1.color.a = 1.0
        m1.color.g = 1.0

        m2 = Marker()
        m2.header.frame_id = "map"
        m2.ns = "stc"
        m2.id = 1
        m2.type = Marker.SPHERE
        m2.action = Marker.ADD
        m2.pose.position = e
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