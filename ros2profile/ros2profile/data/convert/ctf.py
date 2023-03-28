# Copyright 2023 Open Source Robotics Foundation
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

import logging
import lzma
import pickle

from collections import defaultdict
from typing import Dict, Any, List, Union, Callable

import bt2

DictEvent = Dict[str, Any]
DictEvents = List[DictEvent]
CtfEvents = Dict[str, DictEvents]

ConversionFunction = Callable[[str], Union[bool, int, str, List[int]]]

BT2_CONV_FUNC: Dict[str, ConversionFunction] = {
    "context_handle": int,
    "node_handle": int,
    "rmw_publisher_handle": int,
    "rmw_subscription_handle": int,
    "rmw_service_handle": int,
    "rmw_client_handle": int,
    "subscription_handle": int,
    "publisher_handle": int,
    "service_handle": int,
    "client_handle": int,
    "timer_handle": int,
    "rmw_handle": int,
    "node_name": str,
    "start_label": str,
    "goal_label": str,
    "namespace": str,
    "version": str,
    "vpid": int,
    "vtid": int,
    "cpu_id": int,
    "reader": int,
    "writer": int,
    "message": int,
    "callback": int,
    "subscription": int,
    "topic_name": str,
    "service_name": str,
    "procname": str,
    "buffer": int,
    "data": int,
    "timestamp": int,
    "source_timestamp": int,
    "taken": bool,
    "is_intra_process": bool,
    "period": int,
    "handle": int,
    "timeout": int,
    "queue_depth": int,
    "symbol": str,
    "state_machine": int,
    "gid": lambda x: list(map(int, x)),
    "ipb": int,
    "capacity": int,
    "index": int,
    "size": int,
    "overwritten": bool,
    "ptr": int,
    "nmemb": int,
    "in_ptr": int,
    "alignment": int,
    "memptr": int,
}

LTTNG_IGNORE_NAMES = [
    "kmem_mm_page_alloc",
    "kmem_mm_page_free",
    "lttng_ust_statedump:start",
    "lttng_ust_statedump:procname",
    "lttng_ust_lib:load",
    "lttng_ust_lib:build_id",
    "lttng_ust_lib:debug_link",
    "lttng_ust_statedump:bin_info",
    "lttng_ust_statedump:build_id",
    "lttng_ust_statedump:debug_link",
    "lttng_ust_statedump:end",
]


def payload_to_dict(payload) -> DictEvent:
    '''
    Change a babeltrace2 payload into a dictionary of pod types
    '''
    if payload:
        return {k: BT2_CONV_FUNC[k](v) for (k, v) in payload.items()}
    return {}


def event_to_dict(msg: bt2._EventMessageConst) -> DictEvent:
    '''
    Change a babeltrace2 event message into a flattened dictionary
    '''
    meta = {
        "_name": str(msg.event.name),
        "_timestamp": int(msg.default_clock_snapshot.ns_from_origin),
    }

    payload = payload_to_dict(msg.event.payload_field)
    specific_context = payload_to_dict(msg.event.specific_context_field)
    common_context = payload_to_dict(msg.event.common_context_field)
    packet_context = payload_to_dict(msg.event.packet.context_field)
    return {**meta, **payload, **specific_context, **common_context, **packet_context}


def load_ctf(directory: str, ignore_names: List[str] = LTTNG_IGNORE_NAMES) -> CtfEvents:
    msg_it = bt2.TraceCollectionMessageIterator(directory)
    events = defaultdict(list)

    for msg in msg_it:
        if type(msg) is bt2._DiscardedEventsMessageConst:
           logging.warning("Trace lost packets! Data association may fail! Measurements may be missing!")
        if type(msg) is not bt2._EventMessageConst or msg.event.name in ignore_names:
            continue
        pod = event_to_dict(msg)
        del pod["procname"]
        events[pod["_name"]].append(pod)
    return events


def write_events_to_pickle(events: CtfEvents, filename: str) -> None:
    with lzma.open(filename, "wb") as pickle_file:
        pickler = pickle.Pickler(pickle_file, protocol=4)
        pickler.dump(events)


def load_events_from_pickle(filename: str) -> CtfEvents:
    with lzma.open(filename, "rb") as pickle_file:
        pickler = pickle.Unpickler(pickle_file)
        events = pickler.load()
        return events
