from typing import Any, List

from .callback import CallbackEvent
from .timer import Timer
from .subscription import SubscriptionEvent
from .publisher import PublishEvent

class EventSequence():
    def __init__(self, end_event, start_event=None):
        self.start_event = start_event
        self.end_event = end_event
        self.sequence: List[Any] = []

        self._build_sequence(self.end_event, self.start_event)

    def latency(self):
        return self.sequence[0]['timestamp'] - self.sequence[-1]['timestamp']

    def _build_sequence(self, end_event, start_event=None):
        event = end_event
        self.sequence = []

        while event and event != start_event:
            if type(event) is CallbackEvent:
                if type(event.source()) is Timer:
                    self.sequence.append({
                        'node': event.source().node().name(),
                        'event': 'callback_end',
                        'topic': 'timer',
                        'timestamp': event.end()
                    })
                    self.sequence.append({
                        'node': event.source().node().name(),
                        'event': 'callback_start',
                        'topic': 'timer',
                        'timestamp': event.start()
                    })
                else:
                    self.sequence.append({
                        'node': event.source().node().name(),
                        'event': 'callback_end',
                        'topic': event.source().topic_name(),
                        'timestamp': event.end()
                    })
                    self.sequence.append({
                        'node': event.source().node().name(),
                        'event': 'callback_start',
                        'topic': event.source().topic_name(),
                        'timestamp': event.start()
                    })

                event = event.trigger()
            elif type(event) is SubscriptionEvent:
                self.sequence.append({
                    'node': event.source().node().name(),
                    'event': 'rclcpp_take',
                    'topic': event.source().topic_name(),
                    'timestamp': event._rclcpp_init_time
                })
                self.sequence.append({
                    'node': event.source().node().name(),
                    'event': 'rcl_take',
                    'topic': event.source().topic_name(),
                    'timestamp': event._rcl_init_time
                })
                self.sequence.append({
                    'node': event.source().node().name(),
                    'event': 'rmw_take',
                    'topic': event.source().topic_name(),
                    'timestamp': event._rmw_init_time
                })
                event = event.trigger()
            elif type(event) is PublishEvent:
                self.sequence.append({
                    'node': event.source().node().name(),
                    'event': 'rclcpp_pub',
                    'topic': event.source().topic_name(),
                    'timestamp': event._rclcpp_init_time
                })
                self.sequence.append({
                    'node': event.source().node().name(),
                    'event': 'rcl_pub',
                    'topic': event.source().topic_name(),
                    'timestamp': event._rcl_init_time
                })
                self.sequence.append({
                    'node': event.source().node().name(),
                    'event': 'rmw_pub',
                    'topic': event.source().topic_name(),
                    'timestamp': event._rmw_init_time
                })

                event = event.trigger()
            else:
                break
