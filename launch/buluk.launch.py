import os
import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, SetEnvironmentVariable, RegisterEventHandler, TimerAction
from launch.event_handlers import OnProcessExit
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory('buluk_twin')
    share = os.path.dirname(pkg)
    urdf = xacro.process_file(os.path.join(pkg, 'urdf', 'buluk.urdf.xacro')).toxml()
    rviz_cfg = os.path.join(pkg, 'rviz', 'buluk.rviz')

    # Guardar el URDF ya procesado para dárselo a Gazebo
    urdf_path = '/tmp/buluk.urdf'
    with open(urdf_path, 'w') as f:
        f.write(urdf)

    # Forzar Gazebo Fortress y decirle dónde están los STL
    env = [
        SetEnvironmentVariable('GZ_VERSION', 'fortress'),
        SetEnvironmentVariable('IGN_GAZEBO_RESOURCE_PATH', share),
        SetEnvironmentVariable('IGN_GAZEBO_SYSTEM_PLUGIN_PATH', '/opt/ros/humble/lib'),
    ]

    # 1. Gazebo Fortress, mundo vacío
    gazebo = ExecuteProcess(
        cmd=['ign', 'gazebo', '-r', 'empty.sdf', '--render-engine', 'ogre'],
        output='screen')

    # 2. Modelo y TF para RViz
    rsp = Node(package='robot_state_publisher', executable='robot_state_publisher',
               parameters=[{'robot_description': urdf}], output='screen')

    # 3. Crear el robot en Gazebo (directo con la herramienta de Fortress)
    spawn = ExecuteProcess(
        cmd=['ign', 'service', '-s', '/world/empty/create',
             '--reqtype', 'ignition.msgs.EntityFactory',
             '--reptype', 'ignition.msgs.Boolean',
             '--timeout', '20000',
             '--req', f'sdf_filename: "{urdf_path}", name: "buluk"'],
        output='screen')
    spawn_later = TimerAction(period=8.0, actions=[spawn])   # espera a que Gazebo abra

    # 4. Controladores
    jsb = Node(package='controller_manager', executable='spawner',
               arguments=['joint_state_broadcaster'])
    ctrl = Node(package='controller_manager', executable='spawner',
                arguments=['buluk_controller'])

    # 5. RViz y nodo de comandos
    rviz = Node(package='rviz2', executable='rviz2', arguments=['-d', rviz_cfg])
    cmd = Node(package='buluk_twin', executable='commander', output='screen')

    return LaunchDescription(env + [
        gazebo, rsp, spawn_later,
        RegisterEventHandler(OnProcessExit(target_action=spawn, on_exit=[jsb])),
        RegisterEventHandler(OnProcessExit(target_action=jsb, on_exit=[ctrl])),
        RegisterEventHandler(OnProcessExit(target_action=ctrl, on_exit=[rviz, cmd])),
    ])