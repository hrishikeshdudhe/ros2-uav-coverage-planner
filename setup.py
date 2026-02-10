from setuptools import setup

package_name = 'gps_anchor'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/rviz_satellite_launch.py','launch/rviz_satellite_gp_origin_launch.py']), 
        ('share/gps_anchor/rviz', ['rviz/rviz_satellite_config.rviz']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='YOUR NAME',
    maintainer_email='YOUR EMAIL',
    description='GPS anchor package for RViz satellite map',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'fixed_gps_publisher = gps_anchor.fixed_gps_publisher:main',
            'gps_polygon_collector = gps_anchor.gps_polygon_collector:main',
            'map_anchor = gps_anchor.map_anchor:main',
            'fake_gp_origin = gps_anchor.fake_gp_origin:main'
        ],
    },
)

