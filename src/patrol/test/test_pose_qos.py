import unittest

from rclpy.qos import ReliabilityPolicy

from patrol.pose_relay import sensor_qos_profile
from patrol.pose_subscriber import subscription_qos


class TestPoseQoS(unittest.TestCase):
    def test_relay_offers_best_effort_with_depth_ten(self):
        qos = sensor_qos_profile()
        self.assertEqual(qos.reliability, ReliabilityPolicy.BEST_EFFORT)
        self.assertEqual(qos.depth, 10)

    def test_subscriber_reliability_is_configurable(self):
        self.assertEqual(
            subscription_qos('reliable').reliability,
            ReliabilityPolicy.RELIABLE,
        )
        self.assertEqual(
            subscription_qos('best_effort').reliability,
            ReliabilityPolicy.BEST_EFFORT,
        )

    def test_subscriber_reliability_is_case_insensitive(self):
        self.assertEqual(
            subscription_qos('BEST_EFFORT').reliability,
            ReliabilityPolicy.BEST_EFFORT,
        )

    def test_invalid_reliability_is_rejected(self):
        with self.assertRaises(ValueError):
            subscription_qos('sometimes')


if __name__ == '__main__':
    unittest.main()
