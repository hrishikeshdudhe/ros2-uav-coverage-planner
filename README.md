# gps_anchor

ROS2 package for **GPS-based polygon collection and coverage path planning visualization** using RViz and OpenNav Coverage.

This package allows a user to:

1. Visualize GPS data on a satellite map in RViz  
2. Mark a polygon interactively using clicked points  
3. Send the polygon to the coverage planner  
4. Visualize the resulting coverage path

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
│   ├── fake_gp_origin.py
│   ├── fixed_gps_publisher.py
│   ├── map_anchor.py
│   └── gps_polygon_collector.py
│
├── launch/
│   ├── rviz_satellite_launch.py
│   └── rviz_satellite_gp_origin_launch.py
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

This package **does not ship** the RViz satellite plugin or the Coverage Server
These are the repos for the coverage planner and the rviz_satellite plugin needed for the project.
https://github.com/open-navigation/opennav_coverage/tree/humble
https://github.com/nobleo/rviz_satellite/tree/main/

You must clone them **into your workspace**

---

## Nodes

### map_anchor
Anchors the local `map` frame to the first received GPS origin.

**Subscribes**
- `/tarot650/global_position/gp_origin` (`geographic_msgs/GeoPointStamped`)

**Publishes**
- `map`

---

### fixed_gps_publisher
Publishes a stable `/robot_namespace/gps/fix` message so RViz satellite plugins can display imagery.

---

### gps_polygon_collector
Allows interactive point selection and polygon creation in RViz.
By clicking the last point inside a radius of 3 m from the first point, you can close the polygon. 

---

### fake_gp_origin
Testing utility that publishes a fake GPS origin for local development.

---

## Launch Workflows

### 1. Manual Latitude / Longitude Workflow

Use this when **no gp_origin topic is available**.

#### Launch file
```
launch/rviz_satellite_launch.py
```

#### What it does
- Takes latitude, longitude, altitude as launch arguments
- Publishes `/gps/fix` at that location
- Centers RViz satellite imagery on that point
- Anchors the map frame implicitly

#### Run

```bash
ros2 launch gps_anchor rviz_satellite_launch.py   latitude:=48.8584 longitude:=2.2945 altitude:=0.0
```

Use this workflow for:
- Offline testing
- Demos
- Fixed-location experiments

---

### 2. gp_origin based Workflow

Use this when the **system already provides a GPS origin**, e.g. from a drone stack.

#### Launch file
```
launch/rviz_satellite_gp_origin_launch.py
```

#### Nodes started

- `fake_gp_origin`  
  Publishes `/tarot650/global_position/gp_origin` (testing only)

- `map_anchor`  
  Anchors the `map` frame at `gp_origin`

- `fixed_gps_publisher`  
  Republishes GPS fix for RViz satellite

- `gps_polygon_collector`  
  Collects polygon points

- `rviz2`  
  Visualization

#### Run

```bash
ros2 launch gps_anchor rviz_satellite_gp_origin_launch.py
```

In a real system, **remove `fake_gp_origin`** and rely on the actual publisher.

---

## Polygon Collection

### Adding Points

Points are added whenever a GPS fix is received.

Each new point:
- Appears as a red marker
- Is connected with a red line
- Is logged in the terminal
- Last point needs to be in a radius of 3 meters from the first point to successfully close the polygon

### Resettomg the Polygon

Polygon resetting is done via a **ROS 2 service**.

```bash
ros2 service call /robot_namespace/reset_polygon std_srvs/srv/Trigger
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

It includes:
- Satellite imagery display
- Marker and line visualization
- Proper fixed frame (`map`)

The launch file loads it **relative to the package**, so no absolute paths are required.

---

## Build & run

```bash
colcon build
source install/setup.bash
ros2 launch gps_anchor rviz_satellite_gp_origin_launch.py
```

---

## Typical Development Setup

```
workspace/
├── src/
│   ├── gps_anchor/        # This repo (as submodule)
│   ├── rviz_satellite/    # External dependency
│   └── opennav_coverage/  # External dependency
```

---