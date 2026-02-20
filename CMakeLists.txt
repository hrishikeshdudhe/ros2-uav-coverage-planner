cmake_minimum_required(VERSION 3.8)
project(gps_anchor)

# Enable strict warnings for C++ (optional)
if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# --- Find dependencies ---
find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)

find_package(rclcpp REQUIRED)
find_package(rclpy REQUIRED)
find_package(geometry_msgs REQUIRED)

# --- Include headers (for C++ nodes) ---
include_directories(include)

# --- C++ executables section ---
# (Add your C++ nodes here if needed in the future)
# Example:
# add_executable(cpp_node src/cpp_node.cpp)
# ament_target_dependencies(cpp_node rclcpp geometry_msgs)
# install(TARGETS cpp_node DESTINATION lib/${PROJECT_NAME})

# --- Install config, launch, and rviz directories ---
install(DIRECTORY
  launch
  rviz
  DESTINATION share/${PROJECT_NAME}
)

# --- Install Python modules (for imports in Python) ---
ament_python_install_package(${PROJECT_NAME})

# --- Install Python executables (ROS2 nodes) ---
# One install per file to allow RENAME without errors
install(PROGRAMS
  gps_anchor/fake_gp_origin.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME fake_gp_origin
)

install(PROGRAMS
  gps_anchor/fixed_gps_publisher.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME fixed_gps_publisher
)

install(PROGRAMS
  gps_anchor/map_anchor.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME map_anchor
)

install(PROGRAMS
  gps_anchor/gps_polygon_collector.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME gps_polygon_collector
)

# --- Optional: Linting / testing ---
if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

# --- Finalize package ---
ament_package()