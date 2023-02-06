# Copyright 2023 Open Source Robotics Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
import shutil

from launch import LaunchDescription
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode

from tracetools_launch.action import Trace

from . import ProfileConfiguration, get_output_directory


def expand_configuration(profile_config):
    config = ProfileConfiguration(profile_config)

    launch_description = []
    basename = os.path.basename(profile_config)
    basename =  basename.split('.')[0]
    output_dir = get_output_directory(basename)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    shutil.copyfile(profile_config, os.path.join(output_dir, 'config.yaml'))

    for container_name, container_info in config.containers.items():
        components = []
        for node_name in container_info.nodes:
            node = config.nodes[node_name]
            components.append(ComposableNode(
                package=node.package,
                plugin=node.plugin))

        components.append(
            ComposableNode(
                name=container_name + '_monitor',
                package='topnode',
                plugin='ResourceMonitorNode',
                parameters=[{
                    "publish_period_ms": 500,
                    "record_cpu_memory_usage": True,
                    "record_memory_state": True,
                    "record_io_stats": True,
                    "record_stat": True,
                    "record_file": os.path.join(output_dir, container_name + '.mcap')
                }]
            ))

        launch_description.append(
            ComposableNodeContainer(
                name=container_name,
                namespace=container_info.namespace,
                package=container_info.package,
                executable=container_info.type,
                composable_node_descriptions=components))

    launch_description.append(
        Trace(
            session_name='ros2profile-tracing-session',
            base_path=output_dir,
            append_timestamp=False,
            events_kernel=[
              'power_cpu_frequency',
              'kmem_mm_page_alloc',
              'kmem_mm_page_free',
            ],
            events_ust=[
                'lttng_ust_libc:malloc',
                'lttng_ust_libc:calloc',
                'lttng_ust_libc:realloc',
                'lttng_ust_libc:free',
                'lttng_ust_libc:memalign',
                'lttng_ust_libc:posix_memalign',
                '*',
                'dds:*',
                'ros2:*',
            ],
            context_fields={
                'kernel': ['vpid', 'vtid', 'procname'],
                'userspace': ['vpid', 'vtid', 'procname']
            }
        )
    )
    return LaunchDescription(launch_description)
