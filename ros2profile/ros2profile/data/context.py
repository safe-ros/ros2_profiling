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

class Context:
    '''
    Context represents a single rcl_init invokation.
    Typically, there is one context associate with each process in the graph.
    '''
    def __init__(self, context_handle: int, version: str):
        self._handle = context_handle
        self._version = version

    def __repr__(self) -> str:
        return f'<Context handle={self._handle} version={self._version}>'

    @property
    def handle(self) -> int:
        '''
        The identifier of this context
        '''
        return self._handle

    @handle.setter
    def handle(self, value: int) -> None:
        self._handle = value

    @property
    def version(self) -> str:
        '''
        The version of this context
        '''
        return self._version

    @version.setter
    def version(self, value: str) -> None:
        self._version = value
