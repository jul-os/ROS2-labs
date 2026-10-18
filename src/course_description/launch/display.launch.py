from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import FindExecutable


def generate_launch_description():
    dimensions = {
        "base_length": "1.05",
        "base_width": "0.52",
        "body_height": "0.22",
        "body_z": "0.12",
        "wheelbase": "0.8",
        "track": "0.62",
        "wheel_radius": "0.12",
        "wheel_width": "0.07",
        "sensor_x": "0.28",
        "sensor_z": "0.38",
    }
    xacro_path = PathJoinSubstitution(
        [FindPackageShare("course_description"), "urdf", "vehicle.urdf.xacro"]
    )
    xacro_command = [FindExecutable(name="xacro"), " ", xacro_path]
    for name in dimensions:
        xacro_command.extend([" ", name, ":=", LaunchConfiguration(name)])

    rviz_config = PathJoinSubstitution(
        [FindPackageShare("course_description"), "rviz", "vehicle.rviz"]
    )

    return LaunchDescription(
        [
            *[
                DeclareLaunchArgument(name, default_value=value)
                for name, value in dimensions.items()
            ],
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                name="robot_state_publisher",
                output="screen",
                parameters=[{"robot_description": Command(xacro_command)}],
            ),
            Node(
                package="rviz2",
                executable="rviz2",
                name="rviz2",
                arguments=["-d", rviz_config],
                output="screen",
            ),
        ]
    )
