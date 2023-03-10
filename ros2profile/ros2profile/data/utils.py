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

def filter_topics(collection, rosout: bool = False, parameter_events: bool = False):
    ret = []
    for val in collection:
        if not rosout and val.topic_name().find('rosout') >= 0:
            continue
        if not parameter_events and val.topic_name().find('parameter_events') >= 0:
            continue
        ret.append(val)
    return ret
