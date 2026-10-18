#!/usr/bin/env python3
"""Diagnostic subscriber with a launch-configurable reliability policy."""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from turtlesim.msg import Pose


def subscription_qos(reliability):
    """Build the diagnostic subscriber QoS from a launch parameter."""
    policies = {
        'reliable': ReliabilityPolicy.RELIABLE,
        'best_effort': ReliabilityPolicy.BEST_EFFORT,
    }
    reliability = reliability.lower()
    if reliability not in policies:
        raise ValueError("reliability must be either 'reliable' or 'best_effort'")
    return QoSProfile(depth=10, reliability=policies[reliability])


class PoseSubscriber(Node):
    """Log received sensor poses using reliable or best-effort QoS."""

    def __init__(self):
        super().__init__('pose_subscriber')
        self.declare_parameter('reliability', 'reliable')
        reliability = self.get_parameter('reliability').value.lower()
        qos = subscription_qos(reliability)
        self.subscription = self.create_subscription(
            Pose, 'sensor_pose', self._on_pose, qos
        )
        self.get_logger().info(f'Subscribing to sensor_pose with {reliability} QoS')

    def _on_pose(self, message):
        self.get_logger().info(
            f'Received pose: x={message.x:.2f}, y={message.y:.2f}, '
            f'theta={message.theta:.2f}'
        )


def main(args=None):
    rclpy.init(args=args)
    node = PoseSubscriber()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
