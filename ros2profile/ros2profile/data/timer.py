from .callback import Callback
from .graph_entity import GraphEntity

import numpy as np


class Timer(GraphEntity):
    def __init__(self, timer_handle: int, node_handle: int) -> None:
        super().__init__(handle=timer_handle, node_handle=node_handle)

        self._period: int
        self._callback_handle: int
        self._callback: Callback

    @property
    def callback(self) -> Callback:
        """Callback associated with this subscription."""
        return self._callback

    @callback.setter
    def callback(self, value: Callback) -> None:
        self._callback = value

    @property
    def callback_handle(self) -> int:
        """Callback handle associated with this subscription."""
        return self._callback_handle

    @callback_handle.setter
    def callback_handle(self, value: int) -> None:
        self._callback_handle = value

    @property
    def period(self) -> int:
        """Period of the timer."""
        return self._period

    @period.setter
    def period(self, value: int):
        self._period = value

    def mean_period(self) -> int:
        """Return the average period of the timer callback events."""
        calls = np.array([ev.start() for ev in self.callback.events()])
        return np.mean(np.diff(calls))

    def __repr__(self) -> str:
        return f"<Timer handle={self._handle} period={self._period}>"
