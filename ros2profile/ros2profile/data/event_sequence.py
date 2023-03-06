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
            if isinstance(event, CallbackEvent):
                if isinstance(event.source, Timer):
                    self.sequence.append({
                        'node': event.source.node.name,
                        'event': 'ros2:callback_end',
                        'topic': 'timer',
                        'timestamp': event.end()
                    })
                    self.sequence.append({
                        'node': event.source.node.name,
                        'event': 'ros2:callback_start',
                        'topic': 'timer',
                        'timestamp': event.start()
                    })
                else:
                    self.sequence.append({
                        'node': event.source.node.name,
                        'event': 'ros2:callback_end',
                        'topic': event.source.name,
                        'timestamp': event.end()
                    })
                    self.sequence.append({
                        'node': event.source.node.name,
                        'event': 'ros2:callback_start',
                        'topic': event.source.name,
                        'timestamp': event.start()
                    })
                event = event.trigger
            elif isinstance(event, SubscriptionEvent):
                for stamp_key, stamp_value in event._stamps.items():
                    self.sequence.append({
                        'node': event.source.node.name,
                        'event': stamp_key,
                        'topic': event.source.name,
                        'timestamp': stamp_value,
                    })
                event = event.trigger
            elif isinstance(event, PublishEvent):
                for stamp_key, stamp_value in event._stamps.items():
                    self.sequence.append({
                        'node': event.source.node.name,
                        'event': stamp_key,
                        'topic': event.source.name,
                        'timestamp': stamp_value,
                    })
                event = event.trigger
            else:
                break
