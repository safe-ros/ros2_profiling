from rclpy.expand_topic_name import expand_topic_name

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
