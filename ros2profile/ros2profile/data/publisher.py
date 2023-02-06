from rclpy.expand_topic_name import expand_topic_name

from .node import Node

from typing import List


class PublishEvent:
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

        self._trigger = None
        self._source = None

    def trigger(self):
        return self._trigger

    def source(self):
        return self._source

    def __repr__(self) -> str:
        return f'<PublishEvent handle={self._message_handle}>'

class Publisher:
    def __init__(self, publisher_handle):
        self._handle = publisher_handle
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
        self._dds_writer = None

        self._events: List[PublishEvent] = []

    def events(self):
        return self._events

    def handle(self) -> int:
        return self._handle

    def topic_name(self) -> str:
        return expand_topic_name(self._topic_name,
            self._node.name(), self._node.namespace())

    def node(self) -> Node:
        return self._node

    def __repr__(self) -> str:
        return f'<Publisher handle={self._handle} topic_name={self.topic_name()}>'
