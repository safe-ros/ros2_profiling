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

from .publisher import Publisher
from .subscription import Subscription

from typing import List


class Topic:
    def __init__(self, topic_name: str) -> None:
        self._topic_name: str = topic_name
        self._publishers: List[Publisher] = []
        self._subscriptions: List[Subscription] = []

    def add_publisher(self, publisher: Publisher) -> None:
        self._publishers.append(publisher)

    def add_subscription(self, subscription: Subscription) -> None:
        self._subscriptions.append(subscription)

    @property
    def name(self) -> str:
        return self._topic_name

    @property
    def publishers(self) -> List[Publisher]:
        return self._publishers

    @property
    def subscriptions(self) -> List[Subscription]:
        return self._subscriptions

    def __repr__(self) -> str:
        return f'<Topic name={self._topic_name}>'
