import importlib.util
from pathlib import Path
import unittest

from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.conditions import IfCondition


LAUNCH_FILE = Path(__file__).parents[1] / 'launch' / 'patrol.launch.py'
SPEC = importlib.util.spec_from_file_location('patrol_launch', LAUNCH_FILE)
patrol_launch = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(patrol_launch)


class TestPatrolLaunchContract(unittest.TestCase):
    def setUp(self):
        self.description = patrol_launch.generate_launch_description()

    def test_launch_declares_all_required_arguments(self):
        arguments = {
            action.name
            for action in self.description.entities
            if isinstance(action, DeclareLaunchArgument)
        }
        self.assertEqual(
            arguments,
            {'namespace', 'record', 'bag_dir', 'subscriber_reliability'},
        )

    def test_recorder_is_conditional_and_records_mcap(self):
        recorders = [
            action
            for action in self.description.entities
            if isinstance(action, ExecuteProcess)
            and isinstance(action.condition, IfCondition)
        ]
        self.assertEqual(len(recorders), 1)
        recorder = recorders[0]
        self.assertIsInstance(recorder.condition, IfCondition)
        launch_source = LAUNCH_FILE.read_text(encoding='utf-8')
        self.assertIn("'-s', 'mcap'", launch_source)
        self.assertIn("'--topics'", launch_source)


if __name__ == '__main__':
    unittest.main()
