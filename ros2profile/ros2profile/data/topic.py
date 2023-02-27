from .publisher import Publisher
from .subscription import Subscription

from typing import List

class Topic:
    def __init__(self, topic_name: str):
        self._topic_name = topic_name
        self._publishers = []
        self._subscriptions = []

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
