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

from typing import Dict, List, Any
from rclpy.expand_topic_name import expand_topic_name

from .graph_entity import GraphEntity


class PublishEvent:
    def __init__(self, message_handle: int) -> None:
        self._handle: int = message_handle
        self._publisher_handle: int
        self._dds_writer: int

        self._trigger = None
        self._source: Publisher

        self._stamps: Dict[str, int] = {}

    @property
    def publisher_handle(self) -> int:
        return self._publisher_handle

    @publisher_handle.setter
    def publisher_handle(self, value: int) -> None:
        self._publisher_handle = value

    @property
    def dds_writer(self) -> int:
        return self._dds_writer

    @dds_writer.setter
    def dds_writer(self, value: int) -> None:
        self._dds_writer = value

    @property
    def source(self) -> 'Publisher':
        return self._source

    @source.setter
    def source(self, value: 'Publisher') -> None:
        self._source = value

    @property
    def trigger(self) -> Any:
        return self._trigger

    @trigger.setter
    def trigger(self, value: Any):
        self._trigger = value


    def __repr__(self) -> str:
        return f"<PublishEvent handle={self._handle}>"

    def add_stamp(self, key: str, value: int) -> None:
        '''
        Add a timestamp to this graph entity
        '''
        self._stamps[key] = value

    def timestamp(self) -> int:
        return min(self._stamps.values())


class Publisher(GraphEntity):
    def __init__(
        self,
        publisher_handle: int,
        node_handle: int,
        rmw_publisher_handle: int,
        topic_name: str,
        queue_depth: int,
    ) -> None:
        super().__init__(
            handle=publisher_handle,
            rmw_handle=rmw_publisher_handle,
            node_handle=node_handle,
        )
        self._gid: List[int]

        self._topic_name: str = topic_name
        self._queue_depth: int = queue_depth

        self._dds_topic_name: str
        self._dds_writer: int

        self._events: List[PublishEvent] = []

    @property
    def name(self) -> str:
        """
        The identifier of this publisher
        """
        return expand_topic_name(
            self._topic_name, self.node.name, self.node.namespace
        )

    @property
    def gid(self) -> List[int]:
        """
        The underlying DDS GUID of this publisher
        """
        return self._gid

    @gid.setter
    def gid(self, value: List[int]) -> None:
        """
        The underlying DDS GUID of this publisher
        """
        self._gid = value

    @property
    def dds_topic_name(self) -> str:
        """
        The underlying DDS topic name of this publisher
        """
        return self._dds_topic_name

    @dds_topic_name.setter
    def dds_topic_name(self, value: str) -> None:
        self._dds_topic_name = value

    @property
    def dds_writer(self) -> int:
        """
        The underlying DDS writer handle of this publisher
        """
        return self._dds_writer

    @dds_writer.setter
    def dds_writer(self, value: int) -> None:
        self._dds_writer = value

    @property
    def events(self):
        """
        List of events corresponding to this publisher
        """
        return self._events

    def __repr__(self) -> str:
        return f"<Publisher handle={self._handle} topic_name={self.name}>"
