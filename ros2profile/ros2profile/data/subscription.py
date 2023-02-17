from typing import Any, Dict, List

from rclpy.expand_topic_name import expand_topic_name

from .callback import Callback
from .graph_entity import GraphEntity


class SubscriptionEvent:
    def __init__(self, message_handle: int) -> None:
        self._handle: int = message_handle
        self._rmw_subscription_handle: int
        self._dds_reader: int

        self._trigger = None
        self._source: Subscription

        self._stamps: Dict[str, int] = {}

    @property
    def rmw_subscription_handle(self) -> int:
        return self._rmw_subscription_handle

    @rmw_subscription_handle.setter
    def rmw_subscription_handle(self, value: int) -> None:
        self._rmw_subscription_handle = value

    @property
    def dds_reader(self) -> int:
        return self._dds_reader

    @dds_reader.setter
    def dds_reader(self, value: int) -> None:
        self._dds_reader = value

    @property
    def source(self) -> 'Subscription':
        return self._source

    @source.setter
    def source(self, value: 'Subscription') -> None:
        self._source = value

    def trigger(self):
        return self._trigger

    def __repr__(self) -> str:
        return f"<SubscriptionEvent handle={self._handle}>"

    def add_stamp(self, key: str, value: int) -> None:
        '''
        Add a timestamp to this graph entity
        '''
        self._stamps[key] = value

    def timestamp(self) -> int:
        return min(self._stamps.values())


class Subscription(GraphEntity):
    def __init__(
        self,
        subscription_handle: int,
        node_handle: int,
        rmw_subscription_handle: int,
        topic_name: str,
        queue_depth: int,
    ) -> None:
        super().__init__(
            handle=subscription_handle,
            rmw_handle=rmw_subscription_handle,
            node_handle=node_handle
        )
        self._gid: List[int]

        self._reference: int
        self._topic_name: str = topic_name
        self._queue_depth: int = queue_depth

        self._dds_topic_name: str
        self._dds_reader: int

        self._callback_handle: int
        self._callback: Callback
        self._events: List[SubscriptionEvent] = []

    @property
    def name(self) -> str:
        """
        The identifier of this subscription
        """
        return expand_topic_name(
            self._topic_name, self._node.name, self._node.namespace
        )

    @property
    def gid(self) -> List[int]:
        """
        The underlying DDS GUID of this subscription
        """
        return self._gid

    @gid.setter
    def gid(self, value: List[int]) -> None:
        """
        The underlying DDS GUID of this subscription
        """
        self._gid = value

    @property
    def dds_reader_handle(self) -> int:
        """
        The underlying DDS reader of this subscription
        """
        return self._dds_reader

    @dds_reader_handle.setter
    def dds_reader_handle(self, value: int) -> None:
        self._dds_reader = value

    @property
    def dds_topic_name(self) -> str:
        """
        The underlying DDS topic of this subscription
        """
        return self._dds_topic_name

    @dds_topic_name.setter
    def dds_topic_name(self, value: str) -> None:
        self._dds_topic_name = value

    @property
    def callback(self) -> Callback:
        '''
        Callback associated with this subscription
        '''
        return self._callback

    @callback.setter
    def callback(self, value: Callback) -> None:
        self._callback = value

    @property
    def callback_handle(self) -> int:
        '''
        Callback handle associated with this subscription
        '''
        return self._callback_handle

    @callback_handle.setter
    def callback_handle(self, value: int) -> None:
        self._callback_handle = value

    @property
    def reference(self) -> int:
        '''
        Reference associated with the subscription callback
        '''
        return self._reference

    @reference.setter
    def reference(self, value: int) -> None:
        self._reference = value

    @property
    def events(self) -> List[Any]:
        """
        List of events corresponding to this subscription
        """
        return self._events

    def __repr__(self) -> str:
        return f"<Subscription handle={self._handle} topic_name={self.name}>"
