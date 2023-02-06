from .utils import filter_topics

class Node:
    def __init__(self, node_handle: int, node_name: str, namespace: str, rmw_handle: int):
        self._handle = node_handle
        self._name = node_name
        self._namespace = namespace
        self._rmw_handle = rmw_handle

        self._publishers = []
        self._subscriptions = []
        self._timers = []

    def __repr__(self) -> str:
        return f'<Node handle={self._handle} name={self._name}>'

    def name(self) -> str:
        return self._name

    def namespace(self) -> str:
        return self._namespace

    def timers(self):
        return self._timers

    def publishers(self):
        return filter_topics(self._publishers)

    def subscriptions(self):
        return filter_topics(self._subscriptions)
