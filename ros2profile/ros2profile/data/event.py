from abc import ABC, abstractmethod

class EventSource(ABC):
    def __init__(self):
        pass

class Event(ABC):
    def __init__(self):
        self._trigger: Event|None = None
        self._source: EventSource|None = None

    def set_trigger(self, trigger: Event) -> None:
        self._trigger = trigger

    def trigger(self) -> Event:
        """
        The preceeding event that caused this event to occur
        """
        return self._trigger

    def set_source(self, source: EventSource) -> None:
        self._source = source

    def source(self) -> EventSource:
        """
        Graph member that emits these events (eg publisher, subscription, timer)
        """
        return self._source

    def __repr__(self) -> str:
        return f'<Event>'
