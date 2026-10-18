"""Structural checks for the Xacro source and its fixed sensor-frame contract."""

import os
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET


XACRO_NS = "http://www.ros.org/wiki/xacro"
NS = {"xacro": XACRO_NS}
DEFAULT_MODEL = Path(__file__).parents[1] / "urdf" / "vehicle.urdf.xacro"


def read_model():
    path = Path(os.environ.get("URDF_XACRO_PATH", DEFAULT_MODEL))
    return ET.parse(path).getroot()


class VehicleModelContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.robot = read_model()
        cls.args = {
            item.get("name"): item.get("default")
            for item in cls.robot.findall("xacro:arg", NS)
        }

    def test_dimensions_are_parameterized_from_course_model(self):
        expected = {
            "base_length": "1.05",
            "base_width": "0.52",
            "body_height": "0.22",
            "wheelbase": "0.8",
            "track": "0.62",
            "wheel_radius": "0.12",
        }
        for name, value in expected.items():
            with self.subTest(parameter=name):
                self.assertEqual(self.args[name], value)

    def test_base_has_separate_visual_collision_and_valid_inertia(self):
        base = self.robot.find("link[@name='base_link']")
        self.assertIsNotNone(base)
        self.assertIsNotNone(base.find("visual/geometry/box"))
        self.assertIsNotNone(base.find("collision/geometry/box"))
        inertial = base.find("inertial")
        mass = float(inertial.find("mass").get("value"))
        inertia = inertial.find("inertia")
        diagonal = [float(inertia.get(axis)) for axis in ("ixx", "iyy", "izz")]
        self.assertGreater(mass, 0.0)
        self.assertTrue(all(value > 0.0 for value in diagonal))
        self.assertGreaterEqual(diagonal[0] + diagonal[1], diagonal[2])
        self.assertGreaterEqual(diagonal[0] + diagonal[2], diagonal[1])
        self.assertGreaterEqual(diagonal[1] + diagonal[2], diagonal[0])

    def test_sensor_frames_are_fixed_direct_children_with_expected_offset(self):
        expected = {
            "camera_joint": "camera_link",
            "lidar_joint": "lidar_link",
            "imu_joint": "imu_link",
        }
        for joint_name, child_name in expected.items():
            with self.subTest(joint=joint_name):
                joint = self.robot.find(f"joint[@name='{joint_name}']")
                self.assertIsNotNone(joint)
                self.assertEqual(joint.get("type"), "fixed")
                self.assertEqual(joint.find("parent").get("link"), "base_link")
                self.assertEqual(joint.find("child").get("link"), child_name)
                origin = joint.find("origin")
                xyz = origin.get("xyz").split()
                self.assertEqual(len(xyz), 3)
                self.assertEqual(xyz[0], "${sensor_x}")
                self.assertEqual(xyz[1], "0")
                self.assertEqual(xyz[2], "${sensor_z}")
                self.assertEqual(float(self.args["sensor_x"]), 0.28)
                self.assertEqual(float(self.args["sensor_z"]), 0.38)

    def test_fixed_sensor_subtree_is_connected_and_acyclic(self):
        names = {
            item.get("name")
            for item in self.robot.findall("link")
        }
        self.assertTrue({"base_link", "camera_link", "lidar_link", "imu_link"} <= names)
        edges = []
        for joint in self.robot.findall("joint"):
            parent = joint.find("parent").get("link")
            child = joint.find("child").get("link")
            self.assertIn(parent, names)
            self.assertIn(child, names)
            edges.append((parent, child))

        reached = {"base_link"}
        while True:
            expanded = reached | {
                child for parent, child in edges if parent in reached
            } | {
                parent for parent, child in edges if child in reached
            }
            if expanded == reached:
                break
            reached = expanded
        self.assertEqual(reached, names)
        self.assertEqual(len(edges), len(names) - 1)

    def test_wheels_use_parametric_continuous_joints_and_separate_geometry(self):
        macro = self.robot.find("xacro:macro[@name='wheel']", NS)
        self.assertIsNotNone(macro)
        wheel_joint = macro.find("joint")
        self.assertEqual(wheel_joint.get("type"), "continuous")
        self.assertEqual(wheel_joint.find("axis").get("xyz"), "0 1 0")
        self.assertEqual(len(macro.findall("link/visual/geometry/cylinder")), 1)
        self.assertEqual(len(macro.findall("link/collision/geometry/cylinder")), 1)
        cylinder = macro.find("link/visual/geometry/cylinder")
        self.assertEqual(cylinder.get("radius"), "${wheel_radius}")
        self.assertEqual(cylinder.get("length"), "${wheel_width}")
        calls = self.robot.findall("xacro:wheel", NS)
        self.assertEqual(len(calls), 4)
        self.assertEqual(
            {item.get("side") for item in calls},
            {"front_left", "front_right", "rear_left", "rear_right"},
        )


if __name__ == "__main__":
    unittest.main()
