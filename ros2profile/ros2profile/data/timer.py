from .callback import Callback
from .node import Node

import numpy as np

class Timer:
    def __init__(self, timer_handle):
        self._handle = timer_handle
        self._period: int = -1

        self._node: Node = None
        self._node_handle = None

        self._rclcpp_init_time = None
        self._rcl_init_time = None

        self._callback_handle = None
        self._callback: Callback = None

    def handle(self) -> int:
        return self._handle

    def node(self) -> Node:
        return self._node

    def callback(self) -> Callback:
        return self._callback

    def period(self) -> int:
        return self._period

    def mean_period(self) -> int:
        calls = np.array([ev.start() for ev in self.callback().events()])
        return np.mean(np.diff(calls))


    def __repr__(self) -> str:
        return f'<Timer handle={self._handle} period={self._period}>'
