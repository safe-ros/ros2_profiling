# Copyright 2023 Open Source Robotics Foundation, Inc.
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

from .callback import Callback
from .node import Node


class ServiceServer:
    def __init__(self, service_handle: int):
        self._handle = service_handle
        self._node = None
        self._node_handle = None
        self._rmw_handle = None

        self._service_name = None

        self._rclcpp_init_time = None
        self._rcl_init_time = None

        self._callback_handle = None
        self._callback = None

    def handle(self) -> int:
        return self._handle

    def node(self) -> Node:
        return self._node

    def service_name(self):
        return self._service_name

    def callback(self) -> Callback:
        return self._callback

    def __repr__(self) -> str:
        return f'<ServiceServer handle={self._handle} service_name={self.service_name()}>'
