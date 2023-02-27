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

from typing import List, Any


def _prettify(
    original: str,
) -> str:
    """
    Process symbol to make it more readable.

    * remove std::allocator
    * remove std::default_delete
    * bind object: remove placeholder

    :param original: the original symbol
    :return: the prettified symbol
    """
    pretty = original
    # remove spaces
    pretty = pretty.replace(" ", "")
    # allocator
    std_allocator = "_<std::allocator<void>>"
    pretty = pretty.replace(std_allocator, "")
    # default_delete
    std_defaultdelete = "std::default_delete"
    if std_defaultdelete in pretty:
        dd_start = pretty.find(std_defaultdelete)
        template_param_open = dd_start + len(std_defaultdelete)
        # find index of matching/closing GT sign
        template_param_close = template_param_open
        level = 0
        done = False
        while not done:
            template_param_close += 1
            if pretty[template_param_close] == "<":
                level += 1
            elif pretty[template_param_close] == ">":
                if level == 0:
                    done = True
                else:
                    level -= 1
        pretty = pretty[:dd_start] + pretty[(template_param_close + 1):]
    # bind
    std_bind = "std::_Bind<"
    if pretty.startswith(std_bind):
        # remove bind<>
        pretty = pretty.replace(std_bind, "")
        pretty = pretty[:-1]
        # remove placeholder stuff
        placeholder_from = pretty.find("*")
        placeholder_to = pretty.find(")", placeholder_from)
        pretty = (pretty[:placeholder_from] + "?" +
                  pretty[(placeholder_to + 1):])
    # remove dangling comma
    pretty = pretty.replace(",>", ">")
    # restore meaningful spaces
    if pretty.startswith("void"):
        pretty = "void" + " " + pretty[len("void"):]
    if pretty.endswith("const"):
        pretty = pretty[: (len(pretty) - len("const"))] + " " + "const"
    return pretty


class CallbackEvent:
    def __init__(self, callback_handle: int, is_intra_process: bool) -> None:
        self._callback_handle: int = callback_handle
        self._is_intra_process: bool = is_intra_process

        self._callback_start: int
        self._callback_end: int

        self._vpid: int
        self._vtid: int
        self._cpu_id: int

        self._trigger: Any
        self._source: Any

    @property
    def trigger(self) -> Any:
        return self._trigger

    @trigger.setter
    def trigger(self, value: Any):
        self._trigger = value

    @property
    def source(self) -> Any:
        return self._source

    @source.setter
    def source(self, value: Any):
        self._source = value

    @property
    def callback_handle(self) -> int:
        return self._callback_handle

    def start(self) -> int:
        return self._callback_start

    def end(self) -> int:
        return self._callback_end

    def duration(self) -> int:
        return self.end() - self.start()

    def __repr__(self) -> str:
        content = " ".join([
            f"handle={self._callback_handle}",
            f"start={self.start()}",
            f"duration={self.duration()}",
        ])
        return f"<CallbackEvent {content}>"


class Callback:
    """
    Representation of a callback in the computational graph
    """

    def __init__(
        self, callback_handle: int, symbol: str, rclcpp_init_time: int
    ) -> None:
        self._handle: int = callback_handle
        self._symbol: str = symbol
        self._rclcpp_init_time: int = rclcpp_init_time

        self._events: List[CallbackEvent] = []
        self._source: Any = None

    @property
    def handle(self) -> int:
        """
        The identifier of this callback
        """
        return self._handle

    @handle.setter
    def handle(self, value: int) -> None:
        self._handle = value

    @property
    def symbol(self) -> str:
        """
        The callback C++ symbol of this callback
        """
        return self._symbol

    def num_calls(self) -> int:
        return len(self._events)

    def events(self) -> List[CallbackEvent]:
        return self._events

    def __repr__(self) -> str:
        return f"<Callback handle={self._handle}>"
