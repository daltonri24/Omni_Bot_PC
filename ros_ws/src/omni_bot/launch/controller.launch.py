import os

from ament_index_python.packages import get_package_share_directory


from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node



def generate_launch_description():

    joy_linux = Node(
        package='joy_linux',
        executable='joy_linux_node',
    )

    controller_node = Node(
        package='controller_listener',
        executable='controller_command'
    )

    # Launch them all!
    return LaunchDescription([
        joy_linux, 
        controller_node
    ])
