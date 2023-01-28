from rclpy.expand_topic_name import expand_topic_name

from .callback import Callback
from .node import Node

from typing import List

class SubscriptionEvent:
    def __init__(self, message_handle):
        self._message_handle = message_handle

        self._vpid = None
        self._vtid = None
        self._cpu_id = None

        self._rclcpp_init_time = None
        self._rcl_init_time = None
        self._rmw_init_time = None
        self._dds_init_time = None
        self._dds_timestamp = None

        self._dds_reader = None

        self._callback = None

class Subscription:
    def __init__(self, subscription_handle, subscription_reference):
        self._handle = subscription_handle
        self._reference = subscription_reference
        self._node = None
        self._node_handle = None

        self._rmw_handle = None
        self._gid = None

        self._topic_name = None
        self._queue_depth = None

        self._rclcpp_init_time = None
        self._rcl_init_time = None
        self._rmw_init_time = None
        self._dds_init_time = None

        self._dds_topic_name = None
        self._dds_reader = None

        self._events = []

    def handle(self) -> int:
        return self._handle

    def topic_name(self) -> str:
        return expand_topic_name(self._topic_name,
            self._node.name(), self._node.namespace())

    def node(self) -> Node:
        return self._node

    def events(self) -> List[SubscriptionEvent]:
        return self._events

    def callback(self) -> Callback:
        return self._callback

    def __repr__(self) -> str:
        return f'<Subscription handle={self._handle} topic_name={self.topic_name()}>'
