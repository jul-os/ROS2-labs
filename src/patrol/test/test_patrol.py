#!/usr/bin/env python3
"""Tests for the patrol node's compute_twist and validate_publish_hz functions."""

import math
import unittest
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from patrol.patrol import compute_twist, validate_publish_hz


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


if __name__ == '__main__':
    unittest.main()
