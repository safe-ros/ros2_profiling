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
import time
import yaml


def get_output_directory(session_name):
    output_dir = os.environ.get('ROS_HOME')
    if not output_dir:
        output_dir = os.path.join('~', '.ros')
    session_dir = session_name + '-' + time.strftime('%Y%m%d%H%M%S')
    output_dir = os.path.join(output_dir, 'profile', session_dir)
    return os.path.normpath(os.path.expanduser(output_dir))

class Node:
    def __init__(self, name, package, plugin):
        self.name = name
        self.package = package
        self.plugin = plugin

class Container:
    def __init__(self, name, type, nodes, namespace=None, package=None):
        self.name = name
        self.nodes = nodes
        self.type = type
        self.namespace = namespace if namespace else ''
        self.package = package if package else 'rclcpp_components'


class ProfileConfiguration():
    def __init__(self, config_file):
        self.nodes = {}
        self.containers = {}

        config = None
        with open(config_file, 'r') as f:
            config = yaml.load(f, Loader=yaml.SafeLoader)

        if not config:
            return

        for node in config['nodes']:
            n = Node(**node)
            self.nodes[n.name] = n

        for container in config['containers']:
            c = Container(**container)
            self.containers[c.name] = c
