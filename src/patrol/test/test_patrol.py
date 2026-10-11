#!/usr/bin/env python3
"""Tests for the patrol node's compute_twist function."""

import unittest
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from patrol.patrol import compute_twist


class TestComputeTwist(unittest.TestCase):
    """Test cases for compute_twist function."""

    def test_none_pose_returns_zero_twist(self):
        """When no pose is received, return zero Twist."""
        twist = compute_twist(None)
        self.assertIsInstance(twist, Twist)
        self.assertEqual(twist.linear.x, 0.0)
        self.assertEqual(twist.linear.y, 0.0)
        self.assertEqual(twist.linear.z, 0.0)
        self.assertEqual(twist.angular.x, 0.0)
        self.assertEqual(twist.angular.y, 0.0)
        self.assertEqual(twist.angular.z, 0.0)

    def test_pose_returns_patrol_command(self):
        """When a pose is received, return patrol command."""
        pose = Pose()
        pose.x = 5.0
        pose.y = 5.0
        pose.theta = 0.0
        twist = compute_twist(pose)
        self.assertIsInstance(twist, Twist)
        self.assertEqual(twist.linear.x, 0.5)
        self.assertEqual(twist.angular.z, 0.3)

    def test_pose_with_different_values(self):
        """Test with different pose values."""
        pose = Pose()
        pose.x = 1.0
        pose.y = 2.0
        pose.theta = 1.57
        twist = compute_twist(pose)
        self.assertEqual(twist.linear.x, 0.5)
        self.assertEqual(twist.angular.z, 0.3)


if __name__ == '__main__':
    unittest.main()
