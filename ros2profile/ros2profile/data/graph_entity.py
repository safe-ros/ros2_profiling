from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from .node import Node

class GraphEntity:
    """
    Base class of an entity in the ROS computation graph
    """

    def __init__(self, handle: int, node_handle: int, rmw_handle: int = -1) -> None:
        self._handle = handle
        self._rmw_handle = rmw_handle
        self._node_handle = node_handle
        self._node: 'Node'
        self._stamps: Dict[str, int] = {}

    @property
    def handle(self) -> int:
        """
        The identifier of this publisher
        """
        return self._handle

    @property
    def rmw_handle(self) -> int:
        """
        The RMW identifier of this publisher
        """
        return self._rmw_handle

    @property
    def node_handle(self) -> int:
        """
        The identifier of this publisher's node
        """
        return self._node_handle

    @property
    def node(self) -> 'Node':
        """
        The identifier of this publisher
        """
        return self._node

    @node.setter
    def node(self, value: 'Node') -> None:
        """
        The identifier of this publisher
        """
        self._node = value

    def add_stamp(self, key: str, value: int) -> None:
        '''
        Add a timestamp to this graph entity
        '''
        self._stamps[key] = value
