from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, GroupAction, LogInfo
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node, PushRosNamespace


def generate_launch_description():
    namespace = LaunchConfiguration('namespace')
    record = LaunchConfiguration('record')
    bag_dir = LaunchConfiguration('bag_dir')
    subscriber_reliability = LaunchConfiguration('subscriber_reliability')

    sensor_topic = PythonExpression(["'/", namespace, "/sensor_pose'"])

    return LaunchDescription([
        DeclareLaunchArgument(
            'namespace', default_value='robot_a',
            description='Namespace for patrol and pose processing nodes',
        ),
        DeclareLaunchArgument(
            'record', default_value='false',
            description='Record the namespaced sensor_pose topic to MCAP',
        ),
        DeclareLaunchArgument(
            'bag_dir', default_value='evidence/pr05/bag',
            description='Output directory for rosbag2 MCAP recording',
        ),
        DeclareLaunchArgument(
            'subscriber_reliability', default_value='reliable',
            choices=['reliable', 'best_effort'],
            description='Reliability requested by the diagnostic subscriber',
        ),
        LogInfo(msg=['Launching patrol system in namespace /', namespace]),
        Node(
            package='turtlesim', executable='turtlesim_node', name='turtlesim',
            output='screen',
            arguments=['--ros-args', '--log-level', 'info'],
        ),
        GroupAction([
            PushRosNamespace(namespace),
            Node(
                package='patrol', executable='patrol', name='patrol',
                remappings=[
                    ('pose', '/turtle1/pose'),
                    ('cmd_vel', '/turtle1/cmd_vel'),
                ],
                output='screen',
                arguments=['--ros-args', '--log-level', 'info'],
            ),
            Node(
                package='patrol', executable='pose_relay', name='pose_relay',
                remappings=[('pose', '/turtle1/pose')],
                output='screen',
                arguments=['--ros-args', '--log-level', 'info'],
            ),
            Node(
                package='patrol', executable='pose_subscriber',
                name='pose_subscriber',
                parameters=[{'reliability': subscriber_reliability}],
                output='screen',
                arguments=['--ros-args', '--log-level', 'info'],
            ),
        ]),
        LogInfo(msg=['Recording enabled: ', record, ' -> ', bag_dir]),
        ExecuteProcess(
            cmd=[
                'ros2', 'bag', 'record', '-s', 'mcap', '-o', bag_dir,
                '--topics', sensor_topic,
            ],
            condition=IfCondition(record),
            output='screen',
        ),
    ])
