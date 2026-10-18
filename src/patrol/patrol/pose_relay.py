#!/usr/bin/env python3
"""Relay turtlesim pose samples using a sensor-data (best-effort) publisher."""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from turtlesim.msg import Pose


def sensor_qos_profile():
    """Return the best-effort QoS profile offered for sensor data."""
    return QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)


class PoseRelay(Node):
    """Subscribe to ``pose`` and relay it on ``sensor_pose``."""

    def __init__(self):
        super().__init__('pose_relay')
        sensor_qos = sensor_qos_profile()
        self.publisher = self.create_publisher(Pose, 'sensor_pose', sensor_qos)
        self.subscription = self.create_subscription(
            Pose, 'pose', self._on_pose, sensor_qos
        )
        self.get_logger().info('Relaying pose to sensor_pose with best_effort QoS')

    def _on_pose(self, message):
        self.publisher.publish(message)


def main(args=None):
    rclpy.init(args=args)
    node = PoseRelay()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
