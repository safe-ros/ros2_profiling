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
