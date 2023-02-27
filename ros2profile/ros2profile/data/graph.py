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

from typing import List, Dict, Optional

from .callback import Callback
from .context import Context
from .publisher import Publisher
from .subscription import Subscription
from .node import Node
from .topic import Topic
from .timer import Timer

from .utils import filter_topics


class Graph:
    '''
    Represents the ROS 2 computational graph.
    '''
    def __init__(self) -> None:
        self._contexts: Dict[int, Context] = {}
        self._nodes: Dict[int, Node] = {}
        self._callbacks: Dict[int, Callback] = {}
        self._publishers: Dict[int, Publisher] = {}
        self._subscriptions: Dict[int, Subscription] = {}
        self._topics: Dict[str, Topic] = {}
        self._timers: Dict[int, Timer] = {}

    def add_context(self, context: Context) -> None:
        '''
        Add a context (process) to the graph
        '''
        self._contexts[context.handle] = context

    def contexts(self) -> List[Context]:
        '''
        Get a list of the contexts (processes) in the graph
        '''
        return list(self._contexts.values())

    def add_node(self, node: Node) -> None:
        '''
        Add a node to the graph
        '''
        self._nodes[node.handle] = node

    @property
    def nodes(self) -> List[Node]:
        '''
        Get a list of all nodes in the graph
        '''
        return list(self._nodes.values())

    def node_by_handle(self, handle: int) -> Optional[Node]:
        '''
        Get a node from the graph by handle
        '''
        if handle in self._nodes:
            return self._nodes[handle]
        return None

    def node_by_name(self, name: str) -> Optional[Node]:
        '''
        Get a node from the graph by name
        '''
        for node in self._nodes.values():
            if node.name.find(name) >= 0:
                return node
        return None

    def add_publisher(self, publisher: Publisher) -> None:
        '''
        Add a publisher to the graph
        '''
        self._publishers[publisher.handle] = publisher
        node = self.node_by_handle(publisher.node_handle)
        if node:
            publisher.node = node
            node.add_publisher(publisher)

        topic = publisher.name
        if topic not in self._topics:
            self._topics[topic] = Topic(topic)
        self._topics[topic].add_publisher(publisher)

    @property
    def publishers(self) -> List[Publisher]:
        '''
        Get a list of all publishers in the graph
        '''
        return list(self._publishers.values())

    def publisher_by_handle(self, handle: int) -> Optional[Publisher]:
        '''
        Get a publisher using it's handle
        '''
        if handle in self._publishers:
            return self._publishers[handle]
        return None

    def publisher_by_rmw_handle(self, rmw_handle: int) -> Optional[Publisher]:
        '''
        Get a publisher using it's rmw handle
        '''
        for publisher in self._publishers.values():
            if rmw_handle == publisher.rmw_handle:
                return publisher
        return None

    def publisher_by_gid(self, gid: List[int]) -> Optional[Publisher]:
        '''
        Get a publisher using it's DDS GUID
        '''
        for publisher in self._publishers.values():
            if gid == publisher.gid:
                return publisher
        return None

    def publisher_by_topic(self, topic_name: str) -> Optional[Publisher]:
        '''
        Get a publisher using it's topic name
        '''
        for publisher in self._publishers.values():
            if publisher.name.find(topic_name) >= 0:
                return publisher
        return None

    def add_callback(self, callback: Callback) -> None:
        '''
        Add a callback to the ROS graph
        '''
        self._callbacks[callback.handle] = callback

    @property
    def callbacks(self) -> List[Callback]:
        '''
        Retrieve a list of all callbacks in the ROS graph
        '''
        return list(self._callbacks.values())

    def callback_by_handle(self, handle: int) -> Optional[Callback]:
        '''
        Retrieve a callback by it's associated handle
        '''
        if handle in self._callbacks:
            return self._callbacks[handle]
        return None

    def add_subscription(self, subscription: Subscription) -> None:
        '''
        Add a subscription to the graph
        '''
        self._subscriptions[subscription.handle] = subscription
        node = self.node_by_handle(subscription.node_handle)
        if node:
            subscription.node = node
            node.add_subscription(subscription)

        topic = subscription.name
        if topic not in self._topics:
            self._topics[topic] = Topic(topic)
        self._topics[topic].add_subscription(subscription)

    @property
    def subscriptions(self) -> List[Subscription]:
        '''
        Get a list of all subscriptions in the graph
        '''
        return list(self._subscriptions.values())

    def subscription_by_handle(self, handle: int) -> Optional[Subscription]:
        '''
        Get a subscription using it's handle
        '''
        if handle in self._subscriptions:
            return self._subscriptions[handle]
        return None

    def subscription_by_reference(self, reference: int) -> Optional[Subscription]:
        '''
        Get a subscription using it's callback reference
        '''
        for subscription in self._subscriptions.values():
            if subscription.reference == reference:
                return subscription
        return None

    def subscription_by_rmw_handle(self, handle: int) -> Optional[Subscription]:
        '''
        Get a subscription using it's handle
        '''
        for subscription in self._subscriptions.values():
            if subscription.rmw_handle == handle:
                return subscription
        return None

    def subscription_by_gid(self, gid: List[int]) -> Optional[Subscription]:
        '''
        Get a subscription using it's DDS GUID
        '''
        for subscription in self._subscriptions.values():
            if subscription.gid == gid:
                return subscription
        return None

    def add_timer(self, timer: Timer) -> None:
        '''
        Add a timer to the graph
        '''
        self._timers[timer.handle] = timer
        node = self.node_by_handle(timer.node_handle)
        if node:
            timer.node = node
            node.timers.append(timer)

    def timers(self) -> List[Timer]:
        '''
        Get all timers in the graph
        '''
        return list(self._timers.values())

    def timer_by_handle(self, handle: int) -> Optional[Timer]:
        '''
        Get a timer using it's handle
        '''
        if handle in self._timers:
            return self._timers[handle]
        return None

    @property
    def topics(self) -> List[Topic]:
        return list(self._topics.values())

    def topic_by_name(self, topic_name: str) -> Optional[Topic]:
        for topic in self._topics.values():
            if topic.name.find(topic_name) >= 0:
                return topic
