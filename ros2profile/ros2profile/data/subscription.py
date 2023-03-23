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

from typing import Any, Dict, List

from rclpy.expand_topic_name import expand_topic_name

from .callback import Callback
from .graph_entity import GraphEntity


class SubscriptionEvent:
    def __init__(self) -> None:
        self._handle: int
        self._rmw_subscription_handle: int
        self._dds_reader: int

        self._trigger = None
        self._source: Subscription
        self._source_timestamp: int
        self._taken: bool

        self._stamps: Dict[str, int] = {}

    @property
    def message_handle(self) -> int:
        return self._handle

    @message_handle.setter
    def message_handle(self, value: int) -> None:
        self._handle = value

    @property
    def rmw_subscription_handle(self) -> int:
        return self._rmw_subscription_handle

    @rmw_subscription_handle.setter
    def rmw_subscription_handle(self, value: int) -> None:
        self._rmw_subscription_handle = value

    @property
    def dds_reader(self) -> int:
        return self._dds_reader

    @dds_reader.setter
    def dds_reader(self, value: int) -> None:
        self._dds_reader = value

    @property
    def source(self) -> "Subscription":
        return self._source

    @source.setter
    def source(self, value: "Subscription") -> None:
        self._source = value

    @property
    def taken(self) -> bool:
        return self._taken

    @taken.setter
    def taken(self, value: bool) -> None:
        self._taken = value

    @property
    def source_timestamp(self) -> int:
        return self._source_timestamp

    @source_timestamp.setter
    def source_timestamp(self, value: int) -> None:
        self._source_timestamp = value

    @property
    def trigger(self) -> Any:
        return self._trigger

    @trigger.setter
    def trigger(self, value: Any):
        self._trigger = value

    def __repr__(self) -> str:
        return f"<SubscriptionEvent handle={self._handle}>"

    def add_stamp(self, key: str, value: int) -> None:
        """
        Add a timestamp to this graph entity
        """
        self._stamps[key] = value

    def timestamp(self) -> int:
        return min(self._stamps.values())


class Subscription(GraphEntity):
    def __init__(
        self,
        subscription_handle: int,
        node_handle: int,
        rmw_subscription_handle: int,
        topic_name: str,
        queue_depth: int,
    ) -> None:
        super().__init__(
            handle=subscription_handle,
            rmw_handle=rmw_subscription_handle,
            node_handle=node_handle,
        )
        self._gid: List[int]

        self._reference: int
        self._topic_name: str = topic_name
        self._queue_depth: int = queue_depth

        self._dds_topic_name: str
        self._dds_reader: int

        self._callback_handle: int
        self._callback: Callback
        self._events: List[SubscriptionEvent] = []

    @property
    def name(self) -> str:
        """
        The identifier of this subscription.
        """
        return expand_topic_name(
            self._topic_name, self._node.name, self._node.namespace
        )

    @property
    def gid(self) -> List[int]:
        """
        The underlying DDS GUID of this subscription.
        """
        return self._gid

    @gid.setter
    def gid(self, value: List[int]) -> None:
        """
        The underlying DDS GUID of this subscription.
        """
        self._gid = value

    @property
    def dds_reader_handle(self) -> int:
        """
        The underlying DDS reader of this subscription.
        """
        return self._dds_reader

    @dds_reader_handle.setter
    def dds_reader_handle(self, value: int) -> None:
        self._dds_reader = value

    @property
    def dds_topic_name(self) -> str:
        """
        The underlying DDS topic of this subscription.
        """
        return self._dds_topic_name

    @dds_topic_name.setter
    def dds_topic_name(self, value: str) -> None:
        self._dds_topic_name = value

    @property
    def callback(self) -> Callback:
        """
        Callback associated with this subscription.
        """
        return self._callback

    @callback.setter
    def callback(self, value: Callback) -> None:
        self._callback = value

    @property
    def callback_handle(self) -> int:
        """
        Callback handle associated with this subscription.
        """
        return self._callback_handle

    @callback_handle.setter
    def callback_handle(self, value: int) -> None:
        self._callback_handle = value

    @property
    def reference(self) -> int:
        """
        Reference associated with the subscription callback.
        """
        return self._reference

    @reference.setter
    def reference(self, value: int) -> None:
        self._reference = value

    @property
    def events(self) -> List[Any]:
        """
        List of events corresponding to this subscription.
        """
        return self._events

    def __repr__(self) -> str:
        return f"<Subscription handle={self._handle} topic_name={self.name}>"
