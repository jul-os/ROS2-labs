#!/usr/bin/env python3
"""Patrol node for turtlesim.

Subscribes to /turtle1/pose and publishes Twist commands to cmd_vel.
Before receiving the first pose, publishes zero commands.
After receiving a pose, publishes linear.x=0.5, angular.z=0.3.
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose


def compute_twist(pose):
    """Compute Twist command from the last received pose.

    Args:
        pose: turtlesim/msg/Pose or None

    Returns:
        geometry_msgs/msg/Twist
    """
    twist = Twist()
    if pose is None:
        # No pose received yet — zero command
        return twist
    # Default patrol command
    twist.linear.x = 0.5
    twist.angular.z = 0.3
    return twist


class PatrolNode(Node):
    """Node that subscribes to pose and publishes Twist commands."""

    def __init__(self):
        super().__init__('patrol')
        self.last_pose = None
        self.pose_subscription = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10,
        )
        self.cmd_vel_publisher = self.create_publisher(
            Twist,
            'cmd_vel',  # Relative topic — needs remap to /turtle1/cmd_vel
            10,
        )
        self.timer = self.create_timer(0.1, self.timer_callback)

    def pose_callback(self, msg):
        """Store the last received pose."""
        self.last_pose = msg

    def timer_callback(self):
        """Publish Twist command based on the last pose."""
        twist = compute_twist(self.last_pose)
        self.cmd_vel_publisher.publish(twist)


def main(args=None):
    """Main entry point for the patrol node."""
    rclpy.init(args=args)
    node = PatrolNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
