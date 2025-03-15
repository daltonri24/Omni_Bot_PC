import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.actions import IncludeLaunchDescription, GroupAction
from launch.actions import DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node, SetRemap

import xacro


def generate_launch_description():

    # Check if we're told to use sim time
    use_sim_time = LaunchConfiguration('use_sim_time')

    # Process the URDF file
    pkg_path = os.path.join(get_package_share_directory('omni_bot'))
    xacro_file = os.path.join(pkg_path,'description','robot.urdf.xacro')
    robot_description_config = xacro.process_file(xacro_file)
    
    # Create a robot_state_publisher node
    params = {'robot_description': robot_description_config.toxml(), 'use_sim_time': use_sim_time}
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[params]
    )
    
    # ros2 run joint_state_publisher_gui joint_state_publisher_gui
    #oint_state_publisher = Node(
     #   package='joint_state_publisher',
      #  executable='joint_state_publisher_gui',
    #)

    # ros2 run image_transport republish compressed --ros-args --remap in/compressed:=camera/color/image_raw/compressed  --remap out:=image_raw/uncompressed
    node_image_republish = Node(
        package='image_transport',
        executable='republish',
        arguments=['compressed'],
        remappings=[
            ('in/compressed', 'camera/color/image_raw/compressed'),
            ('out', 'image_raw/uncompressed')
        ]
    )

    # ros2 run image_transport republish compressedDepth --ros-args --remap in/compressedDepth:=camera/aligned_depth_to_color/image_raw/compressedDepth  --remap out:=image_raw/uncompressedDepth
    node_imageDepth_republish = Node(
        package='image_transport',
        executable='republish',
        arguments=['compressedDepth'],
        remappings=[
            ('in/compressedDepth', 'camera/aligned_depth_to_color/image_raw/compressedDepth'),
            ('out', 'image_raw/uncompressedDepth')
        ]
    )

    # ros2 launch rtabmap_launch rtabmap.launch.py rtabmap_args:="--delete_db_on_start" depth_topic:=/image_raw/uncompressedDepth rgb_topic:=/image_raw/uncompressed camera_info_topic:=/camera/color/camera_info approx_sync:=true frame_id:=base_link rviz:=true
    rtabmap_launch = GroupAction(
        actions=[
            SetRemap(src='/rtabmap/map',dst='/map'),
    
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory('rtabmap_launch'), 'launch', 'rtabmap.launch.py')]),
                launch_arguments={
                    'rtabmap_args': '--delete_db_on_start  --Grid/RangeMax 2.5  --Grid/NoiseFilteringMinNeighbors 10  --Grid/MaxObstacleHeight 2.5',
                    'depth_topic': '/image_raw/uncompressedDepth',
                    'rgb_topic': '/image_raw/uncompressed',
                    'camera_info_topic': '/camera/color/camera_info',
                    'approx_sync': 'true',
                    'frame_id': 'base_link',
                    'rviz': 'true',
                    'cloud_noise_filtering_radius': '0.05',
                    "cloud_noise_filtering_min_neighbors": '5'
                }.items()
            )
        ]
    )


    # Launch!
    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use sim time if true'),

        node_robot_state_publisher,
        #joint_state_publisher,
        node_image_republish,
        node_imageDepth_republish,
        rtabmap_launch
    ])
