from typing import List

from .callback import Callback
from .context import Context
from .publisher import Publisher
from .subscription import Subscription
from .node import Node
from .topic import Topic
from .timer import Timer

from .utils import filter_topics


class Graph:
    def __init__(self):
        self._contexts = {}
        self._nodes = {}
        self._callbacks = {}
        self._publishers = {}
        self._subscriptions = {}
        self._topics = {}
        self._timers = {}

    def add_context(self, context: Context):
        self._contexts[context._handle] = context

    def contexts(self) -> List[Context]:
        return list(self._contexts.values())

    def add_node(self, node: Node):
        self._nodes[node._handle] = node

    def nodes(self, node_name=None) -> List[Node]:
        if node_name:
            ret = []
            for node in self._nodes.values():
                if node.name().find(node_name) >= 0:
                    ret.append(node)
            return ret
        else:
            return list(self._nodes.values())

    def add_callback(self, callback: Callback) -> None:
        self._callbacks[callback._handle] = callback

    def add_publisher(self, publisher: Publisher) -> None:
        self._publishers[publisher.handle()] = publisher

        topic = publisher.topic_name()
        if topic not in self._topics:
            self._topics[topic] = Topic(topic)
        self._topics[topic].add_publisher(publisher)
        self._nodes[publisher._node_handle]._publishers.append(publisher)

    def publishers(self, rosout=False, parameter_events=False) -> List[Publisher]:
        return filter_topics(self._publishers.values(), rosout, parameter_events)

    def add_subscription(self, subscription: Subscription):
        self._subscriptions[subscription.handle()] = subscription
        topic = subscription.topic_name()
        if topic not in self._topics:
            self._topics[topic] = Topic(topic)
        self._topics[topic].add_subscription(subscription)
        self._nodes[subscription._node_handle]._subscriptions.append(subscription)

    def subscriptions(self, rosout=False, parameter_events=False) -> List[Subscription]:
        return filter_topics(self._subscriptions.values(), rosout, parameter_events)

    def topics(self, rosout=False, parameter_events=False) -> List[Topic]:
        return filter_topics(self._topics.values(), rosout, parameter_events)

    def add_timer(self, timer: Timer) -> None:
        self._timers[timer.handle()] = timer
        if timer._node_handle in self._nodes:
            self._nodes[timer._node_handle]._timers.append(timer)

    def timers(self) -> List[Timer]:
        return list(self._timers.values())
