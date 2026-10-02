# ROS2 Buluk Twin

Digital twin of the FRC robot **Buluk** in ROS 2 Humble: URDF model, physics simulation in
Gazebo Fortress, control through `ros2_control`, and visualization in RViz2, all started from a
single launch file.

## The Robot

**Buluk** is an FRC competition robot that collects game pieces with an intake, transports
them, and shoots them using an adjustable-angle mechanism.

- **Degrees of freedom:** 6
- **Base:** fixed to the world (`world → base_link`)

| Joint | Type | Axis | Limits | Function |
|---|---|---|---|---|
| `intake_arm_joint` | revolute | X | −110° to 0° | Lowers and raises the intake arm |
| `angulator_joint` | revolute | X | 88° to 138° | Adjusts the shooting angle |
| `tambor_joint` | continuous | X | – | Drum that transports game pieces |
| `box_joint` | prismatic | Y | −0.23 to 0 m | Sliding box |
| `roller1_joint` | continuous | X | – | Intake roller |
| `roller2_joint` | continuous | X | – | Internal roller |

## Requirements

- Ubuntu 22.04
- ROS 2 Humble
- Gazebo Fortress (`ign gazebo`)

```bash
sudo apt install ros-humble-ros2-control ros-humble-ros2-controllers \
  ros-humble-ign-ros2-control ros-humble-forward-command-controller \
  ros-humble-joint-state-broadcaster ros-humble-xacro \
  ros-humble-robot-state-publisher ros-humble-joint-state-publisher-gui
```

## Build

```bash
mkdir -p ~/buluk_ws/src
cd ~/buluk_ws/src
git clone https://github.com/rodricrz2307/ROS2-Buluk-Twin.git buluk_twin
cd ~/buluk_ws
colcon build
source install/setup.bash
```

## Run

```bash
ros2 launch buluk_twin buluk.launch.py
```

The launch file starts everything in order:

1. Opens **Gazebo Fortress** with an empty world.
2. Publishes the robot model and TFs with `robot_state_publisher`.
3. Spawns the robot in Gazebo from the URDF.
4. Loads the `joint_state_broadcaster` and `buluk_controller` controllers.
5. Opens **RViz2** with the saved configuration.
6. Starts the `commander` node, which moves the robot.

## ROS 2 Architecture

```
commander ──/buluk_controller/commands──▶ buluk_controller ──▶ Gazebo (ign_ros2_control)
                                                                    │
RViz2 ◀── /tf ◀── robot_state_publisher ◀── /joint_states ◀── joint_state_broadcaster
```

| Topic | Type | Description |
|---|---|---|
| `/buluk_controller/commands` | `std_msgs/Float64MultiArray` | Target position for the 6 joints |
| `/joint_states` | `sensor_msgs/JointState` | Actual position and velocity of each joint |
| `/tf` | `tf2_msgs/TFMessage` | Transforms between links |
| `/robot_description` | `std_msgs/String` | Robot URDF model |

### `commander` Node

Publishes the **"Animated robot"** routine at 50 Hz:

- `intake_arm`, `angulator`, and `box` move back and forth with a smooth (cosine) profile
  every 3 s.
- `tambor` and the rollers spin continuously, one turn every 1.5 s.

Array order: `[intake_arm, angulator, tambor, box, roller1, roller2]`.

## Package Structure

```
buluk_twin/
├── buluk_twin/commander.py      # Node that sends motion commands
├── config/controllers.yaml      # ros2_control configuration
├── launch/buluk.launch.py       # Single launch file
├── meshes/                      # Robot STL parts
├── rviz/buluk.rviz              # RViz2 configuration
├── urdf/buluk.urdf.xacro        # Robot model + ros2_control
├── package.xml
└── setup.py
```

## Modeling Notes

- The STL files are in meters and already in their assembled position. Each joint is placed
  at its pivot, and the `<visual>` origin is offset by the negative pivot so each part stays
  in place.
- Collisions use simple boxes and cylinders to keep the simulation stable.
- The `angulator` starts at 1.536 rad (88°), inside its range, to avoid jumps at startup.
- Meshes were simplified to about 100k triangles so Gazebo and RViz run smoothly.

## Inspecting the Data

```bash
ros2 topic echo /joint_states
ros2 topic hz /buluk_controller/commands
ros2 run tf2_tools view_frames
```

## Author

Rodrigo Cruz Paredes, Student at PrepaTec CEM
