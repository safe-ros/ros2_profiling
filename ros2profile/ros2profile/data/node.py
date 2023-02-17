from typing import List

from .publisher import Publisher
from .subscription import Subscription
from .timer import Timer


class Node:
    """
    Representation of a single node in the computational graph
    """

    def __init__(
        self, node_handle: int, node_name: str, namespace: str, rmw_handle: int
    ) -> None:
        self._handle: int = node_handle
        self._name: str = node_name
        self._namespace: str = namespace
        self._rmw_handle: int = rmw_handle

        self._publishers: List[Publisher] = []
        self._subscriptions: List[Subscription] = []
        self._timers: List[Timer] = []

    def __repr__(self) -> str:
        return f"<Node handle={self._handle} name={self._name}>"

    @property
    def handle(self) -> int:
        """
        The identifier of this node
        """
        return self._handle

    @handle.setter
    def handle(self, value: int) -> None:
        self._handle = value

    @property
    def name(self) -> str:
        """
        The name of this node
        """
        return self._name

    @property
    def namespace(self) -> str:
        """
        The namespace of this node
        """
        return self._namespace

    @property
    def timers(self) -> List[Timer]:
        return self._timers

    def add_publisher(self, publisher: Publisher) -> None:
        self._publishers.append(publisher)

    @property
    def publishers(self) -> List[Publisher]:
        return self._publishers

    def add_subscription(self, subscription: Subscription) -> None:
        self._subscriptions.append(subscription)

    @property
    def subscriptions(self) -> List[Subscription]:
        return self._subscriptions
