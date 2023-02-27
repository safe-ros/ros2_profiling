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

from .graph_entity import GraphEntity


class ServiceServer(GraphEntity):
    def __init__(self, service_handle: int, node_handle: int, rmw_service_handle: int):
        super().__init__(
            handle=service_handle,
            rmw_handle=rmw_service_handle,
            node_handle=node_handle,
        )

        self._service_name: str
        self._callback_handle: int
        self._callback: Callback

    @property
    def name(self) -> str:
        """
        The identifier of this service server
        """
        return self._service_name

    @name.setter
    def name(self, value: str) -> None:
        self._service_name = value

    @property
    def callback(self) -> Callback:
        """
        Callback associated with this service server.
        """
        return self._callback

    @callback.setter
    def callback(self, value: Callback) -> None:
        self._callback = value

    @property
    def callback_handle(self) -> int:
        """
        Callback handle associated with this service server.
        """
        return self._callback_handle

    @callback_handle.setter
    def callback_handle(self, value: int) -> None:
        self._callback_handle = value

    def __repr__(self) -> str:
        return f"<ServiceServer handle={self._handle} service_name={self.name}>"
