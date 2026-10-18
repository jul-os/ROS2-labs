#!/usr/bin/env python3
"""Tests for the patrol node's compute_twist and validate_publish_hz functions."""

import math
import unittest

import rclpy
from rclpy.parameter import Parameter
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from patrol.patrol import PatrolNode, compute_twist, validate_publish_hz


class TestComputeTwist(unittest.TestCase):
    """Test cases for compute_twist function."""

    def test_none_pose_returns_zero_twist(self):
        """When no pose is received, return zero Twist."""
        twist = compute_twist(None)
        self.assertIsInstance(twist, Twist)
        self.assertEqual(twist.linear.x, 0.0)
        self.assertEqual(twist.angular.z, 0.0)

    def test_pose_returns_default_patrol_command(self):
        """When a pose is received, return default patrol command."""
        pose = Pose()
        pose.x = 5.0
        pose.y = 5.0
        pose.theta = 0.0
        twist = compute_twist(pose)
        self.assertIsInstance(twist, Twist)
        self.assertEqual(twist.linear.x, 0.5)
        self.assertEqual(twist.angular.z, 0.3)

    def test_pose_with_custom_speeds(self):
        """Test with custom linear_speed and turn_rate."""
        pose = Pose()
        pose.x = 1.0
        pose.y = 2.0
        pose.theta = 1.57
        twist = compute_twist(pose, linear_speed=0.8, turn_rate=-0.5)
        self.assertEqual(twist.linear.x, 0.8)
        self.assertEqual(twist.angular.z, -0.5)


class TestValidatePublishHz(unittest.TestCase):
    """Test cases for validate_publish_hz function."""

    def test_valid_frequency_10hz(self):
        """10 Hz is valid."""
        is_valid, reason = validate_publish_hz(10.0)
        self.assertTrue(is_valid)

    def test_valid_frequency_5hz(self):
        """5 Hz is valid."""
        is_valid, reason = validate_publish_hz(5.0)
        self.assertTrue(is_valid)

    def test_valid_frequency_1hz(self):
        """1 Hz is valid (lower bound)."""
        is_valid, reason = validate_publish_hz(1.0)
        self.assertTrue(is_valid)

    def test_valid_frequency_30hz(self):
        """30 Hz is valid (upper bound)."""
        is_valid, reason = validate_publish_hz(30.0)
        self.assertTrue(is_valid)

    def test_invalid_frequency_zero(self):
        """0 Hz is invalid."""
        is_valid, reason = validate_publish_hz(0.0)
        self.assertFalse(is_valid)
        self.assertIn("must be in [1, 30]", reason)

    def test_invalid_frequency_negative(self):
        """Negative frequency is invalid."""
        is_valid, reason = validate_publish_hz(-5.0)
        self.assertFalse(is_valid)
        self.assertIn("must be in [1, 30]", reason)

    def test_invalid_frequency_nan(self):
        """NaN frequency is invalid."""
        is_valid, reason = validate_publish_hz(float('nan'))
        self.assertFalse(is_valid)
        self.assertIn("must be finite", reason)

    def test_invalid_frequency_inf(self):
        """Infinite frequency is invalid."""
        is_valid, reason = validate_publish_hz(float('inf'))
        self.assertFalse(is_valid)
        self.assertIn("must be finite", reason)

    def test_invalid_frequency_too_high(self):
        """Above 30 Hz is invalid."""
        is_valid, reason = validate_publish_hz(50.0)
        self.assertFalse(is_valid)
        self.assertIn("must be in [1, 30]", reason)


class TestPatrolNode(unittest.TestCase):
    """Test cases for the node's parameter handling (no graph interaction needed)."""

    @classmethod
    def setUpClass(cls):
        if not rclpy.ok():
            rclpy.init(args=None)
        cls.node = PatrolNode()

    @classmethod
    def tearDownClass(cls):
        cls.node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

    def _set(self, name, value):
        """Apply one parameter change through the node's own callback."""
        results = self.node.set_parameters([Parameter(name, value=value)])
        return results[0]

    def test_declared_parameters_have_defaults(self):
        """Linear 0.5, turn 0.3, publish 10 Hz are declared at startup."""
        self.assertEqual(self.node.get_parameter('linear_speed').value, 0.5)
        self.assertEqual(self.node.get_parameter('turn_rate').value, 0.3)
        self.assertEqual(self.node.get_parameter('publish_hz').value, 10.0)

    def test_publish_hz_change_recreates_timer(self):
        """A valid 10 -> 5 Hz change rebuilds the timer with period 1/hz."""
        old_timer = self.node.timer
        result = self._set('publish_hz', 5.0)
        self.assertTrue(result.successful)
        self.assertEqual(self.node.publish_hz, 5.0)
        self.assertIsNot(self.node.timer, old_timer)
        self.assertEqual(self.node.timer.timer_period_ns, int(1e9 / 5.0))
        self.assertFalse(self.node.timer.is_canceled())

    def test_publish_hz_zero_rejected_state_kept(self):
        """Zero is rejected: old frequency and running timer are preserved."""
        self._set('publish_hz', 5.0)
        old_timer = self.node.timer
        result = self._set('publish_hz', 0.0)
        self.assertFalse(result.successful)
        self.assertIn("[1, 30]", result.reason)
        self.assertEqual(self.node.publish_hz, 5.0)
        self.assertIs(self.node.timer, old_timer)
        self.assertFalse(self.node.timer.is_canceled())

    def test_publish_hz_negative_rejected(self):
        """Negative frequency is rejected."""
        self._set('publish_hz', 5.0)
        result = self._set('publish_hz', -2.0)
        self.assertFalse(result.successful)
        self.assertEqual(self.node.publish_hz, 5.0)

    def test_publish_hz_nan_rejected(self):
        """NaN frequency is rejected as non-finite."""
        self._set('publish_hz', 5.0)
        result = self._set('publish_hz', float('nan'))
        self.assertFalse(result.successful)
        self.assertEqual(self.node.publish_hz, 5.0)

    def test_linear_speed_range(self):
        """linear_speed accepts [0, 1] and rejects out-of-range values."""
        self.assertTrue(self._set('linear_speed', 0.8).successful)
        self.assertEqual(self.node.linear_speed, 0.8)
        self.assertFalse(self._set('linear_speed', 2.0).successful)
        self.assertFalse(self._set('linear_speed', -0.1).successful)
        self.assertFalse(self._set('linear_speed', float('nan')).successful)
        self.assertEqual(self.node.linear_speed, 0.8)

    def test_turn_rate_range(self):
        """turn_rate accepts [-1, 1] and rejects out-of-range values."""
        self.assertTrue(self._set('turn_rate', -0.5).successful)
        self.assertEqual(self.node.turn_rate, -0.5)
        self.assertFalse(self._set('turn_rate', 1.5).successful)
        self.assertFalse(self._set('turn_rate', float('nan')).successful)
        self.assertEqual(self.node.turn_rate, -0.5)


if __name__ == '__main__':
    unittest.main()
