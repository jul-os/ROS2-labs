#!/usr/bin/env python3
"""Patrol node for turtlesim with configurable parameters.

Subscribes to /turtle1/pose and publishes Twist commands to cmd_vel.
Parameters: linear_speed, turn_rate, publish_hz.
"""

import math
import rclpy
from rcl_interfaces.msg import SetParametersResult
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose


def validate_publish_hz(value):
    """Validate publish_hz parameter.

    Args:
        value: proposed value for publish_hz

    Returns:
        tuple: (is_valid: bool, reason: str)
    """
    if not math.isfinite(value):
        return False, f"publish_hz must be finite, got {value}"
    if value < 1.0 or value > 30.0:
        return False, f"publish_hz must be in [1, 30], got {value}"
    return True, "ok"


def compute_twist(pose, linear_speed=0.5, turn_rate=0.3):
    """Compute Twist command from the last received pose.

    Args:
        pose: turtlesim/msg/Pose or None
        linear_speed: linear velocity in m/s
        turn_rate: angular velocity in rad/s

    Returns:
        geometry_msgs/msg/Twist
    """
    twist = Twist()
    if pose is None:
        return twist
    twist.linear.x = linear_speed
    twist.angular.z = turn_rate
    return twist


class PatrolNode(Node):
    """Node that subscribes to pose and publishes Twist commands."""

    def __init__(self):
        super().__init__('patrol')

        # Declare parameters
        self.declare_parameter('linear_speed', 0.5)
        self.declare_parameter('turn_rate', 0.3)
        self.declare_parameter('publish_hz', 10.0)

        # Get initial values
        self.linear_speed = self.get_parameter('linear_speed').value
        self.turn_rate = self.get_parameter('turn_rate').value
        self.publish_hz = self.get_parameter('publish_hz').value

        self.last_pose = None
        self.pose_subscription = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10,
        )
        self.cmd_vel_publisher = self.create_publisher(
            Twist,
            'cmd_vel',
            10,
        )
        self.timer = self.create_timer(1.0 / self.publish_hz, self.timer_callback)

        # Add parameter callback
        self.add_on_set_parameters_callback(self.parameter_callback)

    def parameter_callback(self, params):
        """Handle parameter changes."""
        for param in params:
            if param.name == 'linear_speed':
                if math.isfinite(param.value) and 0.0 <= param.value <= 1.0:
                    self.linear_speed = param.value
                    self.get_logger().info(f"linear_speed set to {param.value}")
                else:
                    self.get_logger().warn(f"Invalid linear_speed: {param.value}")
                    return SetParametersResult(successful=False)

            elif param.name == 'turn_rate':
                if math.isfinite(param.value) and -1.0 <= param.value <= 1.0:
                    self.turn_rate = param.value
                    self.get_logger().info(f"turn_rate set to {param.value}")
                else:
                    self.get_logger().warn(f"Invalid turn_rate: {param.value}")
                    return SetParametersResult(successful=False)

            elif param.name == 'publish_hz':
                is_valid, reason = validate_publish_hz(param.value)
                if is_valid:
                    self.publish_hz = param.value
                    # Recreate timer with new period
                    self.timer.cancel()
                    self.timer = self.create_timer(1.0 / self.publish_hz, self.timer_callback)
                    self.get_logger().info(f"publish_hz set to {param.value}")
                else:
                    self.get_logger().warn(f"Invalid publish_hz: {reason}")
                    return rclpy.parameter.SetParametersResult(successful=False)

        return SetParametersResult(successful=True)

    def pose_callback(self, msg):
        """Store the last received pose."""
        self.last_pose = msg

    def timer_callback(self):
        """Publish Twist command based on the last pose."""
        twist = compute_twist(self.last_pose, self.linear_speed, self.turn_rate)
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
