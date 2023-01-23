from setuptools import find_packages
from setuptools import setup

package_name = 'ros2profile'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['ros2cli'],
    zip_safe=True,
    maintainer='Michael Carroll',
    maintainer_email='michael@openrobotics.org',
    description='Generate analysis and assert performance of a system under test',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'ros2cli.command': [
            'profile = ros2profile.command.profile:ProfileCommand',
        ],
        'ros2cli.extension_point': [
            'ros2profile.verb = ros2profile.verb:VerbExtension'
        ],
        'ros2profile.verb': [
            'launch = ros2profile.verb.launch:LaunchVerb',
            'process = ros2profile.verb.process:ProcessVerb',
            'run_test = ros2profile.verb.run_test:RunTestVerb'
        ]
    },
)
