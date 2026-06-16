# gps_anchor

ROS2 package for **GPS-based polygon collection and coverage path planning visualization** using RViz and OpenNav Coverage.

This package allows a user to:

1. Visualize GPS data on a satellite map in RViz  
2. Mark a polygon interactively using clicked points  
3. Send the polygon to two different coverage planners, the first being an open source planner named Opennav Coverage Planner. The other is a custom node which is an STC (Spawn Tree Coverage) based coverage planner.  
4. Visualize the resulting coverage paths from both planners for comparison.

---

## Repository Structure
All future C++ source code will be added with the `src` folder, and the headers for the code will be added with `include/gps_anchor/` when necessary
```
gps_anchor/
├── CMakeLists.txt
├── package.xml
├── README.md
│
├── include/
│   └── gps_anchor/
│       └── (C++ headers, if any)
│
├── src/
│   └── (C++ source files, if any)
│
├── gps_anchor/
│   ├── __init__.py
│   ├── coverage_client.py
│   ├── fake_gp_origin.py
│   ├── fixed_gps_publisher.py
│   └── gps_polygon_collector.py
│   ├── stc_coverage_planner.py
│
├── launch/
│   └── rviz_coverage_launch.py
|   └── rviz_coverage_offline_launch.py
│   └── rviz_satellite_gp_origin_launch.py
│   ├── rviz_satellite_launch.py
│
├── rviz/
│   └── (RViz configuration files)
```

---

## Dependencies

### ROS2 dependencies

- `rclpy`
- `geometry_msgs`
- `sensor_msgs`
- `visualization_msgs`
- `nav_msgs`
- `std_srvs`
- `tf2_ros`

### External Packages

This package **does not ship** the RViz satellite plugin or the Coverage Server. 
These are the repos for the coverage planner and the rviz_satellite plugin needed for the project.

https://github.com/open-navigation/opennav_coverage/tree/humble
https://github.com/nobleo/rviz_satellite/tree/main/

You must clone them **into your workspace**


# Nodes

### GP Origin (`fake_gp_origin`)
Publishes a fixed `GeoPointStamped` message on:
- `/tarot650/global_postion/gp_origin`

This node simulates the GPS origin of a drone and is mainly used for testing

---

### Polygon Collector (`gps_polygon_collector`)
Collects clicked RViz points and forms a polygon.

- Subscribes: `/clicked_point`
- Publishes:
  - `collected_polygon` (final polygon)
  - `polygon_marker` (visualization)
  - `polygon_ready` (trigger planners)
- Auto-closes polygon when first point is reached
- Reset via `coverage_reset`

---

### STC Coverage Planner (`stc_coverage_planner`)
Generates coverage path using grid + DFS traversal.

- Subscribes: polygon + trigger topics
- Publishes:
  - `coverage_path_stc`
  - `coverage_markers_stc`

---

### Coverage Client (`coverage_client`)
Interfaces with OpenNav Coverage action server.

- Sends polygon as action goal
- Receives optimized coverage path
- Publishes:
  - `coverage_path_opennav`
  - `coverage_markers_opennav`
- Reset via `coverage_reset`

---

### Fixed GPS Publisher (`fixed_gps_publisher`)
Simulates GPS input for testing.

- Subscribes: `/tarot650/global_position/gp_origin`
- Publishes: `gps/fix`

---

# Run

### 1. Online launch

```bash
ros2 launch gps_anchor rviz_coverage_launch.py
```
---

### 2. Offline launch

```bash
ros2 launch gps_anchor rviz_coverage_offline_launch.py
```
---

### Resetting the Polygon

Polygon resetting is done via a **ROS2 topic**.

```bash
ros2 topic pub /robot_namespace/coverage_reset std_msgs/msg/Empty "{}" --once
```

Rules:
- Minimum 3 points required
- Last point is connected to the first
- Polygon becomes visually closed in RViz

---

## RViz Configuration

The RViz config file is located at:

```
gps_anchor/rviz/rviz_satellite_config.rviz
```

## Build & run

```bash
colcon build
source install/setup.bash
ros2 launch gps_anchor rviz_coverage_launch.py
```
---