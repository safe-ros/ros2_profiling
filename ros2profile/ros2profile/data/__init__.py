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

from typing import Dict, Any, List, Optional

from collections import defaultdict

import logging
import os

from .callback import Callback, CallbackEvent
from .context import Context
from .node import Node
from .graph import Graph
from .publisher import Publisher, PublishEvent, IPPublishEvent, MessageInBuffer
from .subscription import Subscription, SubscriptionEvent, IpSubscriptionEvent
from .timer import Timer
from . import constants

logging.basicConfig()
logger = logging.getLogger("ros2profile")

try:
    import coloredlogs
except ImportError:
    pass
else:
    log_format = os.environ.get(
        "COLOREDLOGS_LOG_FORMAT", "%(name)s %(levelname)s %(message)s"
    )
    coloredlogs.install(level=1, logger=logger, fmt=log_format)


RawEvent = Dict[str, Any]
RawEvents = List[RawEvent]
RawEventCollection = Dict[str, RawEvents]


def build_graph(
    event_data: RawEventCollection,
    process_timer_events: bool = True,
    process_callback_events: bool = True,
    process_publish_events: bool = True,
    process_subscription_events: bool = True,
) -> Graph:
    ret = Graph()

    context_events = event_data[constants.RCL_INIT]
    _build_contexts(ret, context_events)

    node_events = event_data[constants.RCL_NODE_INIT]
    _build_nodes(ret, node_events)

    callback_events = event_data[constants.RCLCPP_CALLBACK_REGISTER]
    _build_callbacks(ret, callback_events)

    rcl_publisher_events = event_data[constants.RCL_PUBLISHER_INIT]
    rmw_publisher_events = event_data[constants.RMW_PUBLISHER_INIT]
    dds_writer_events = event_data[constants.DDS_CREATE_WRITER]
    _build_publishers(
        ret, rcl_publisher_events, rmw_publisher_events, dds_writer_events
    )

    rclcpp_events = event_data[constants.RCLCPP_SUBSCRIPTION_INIT]
    rclcpp_cb_events = event_data[constants.RCLCPP_SUBSCRIPTION_CALLBACK_ADDED]
    rcl_events = event_data[constants.RCL_SUBSCRIPTION_INIT]
    rmw_events = event_data[constants.RMW_SUBSCRIPTION_INIT]
    dds_events = event_data[constants.DDS_CREATE_READER]
    ipb_to_subscription_events = event_data[constants.RCLCPP_IPB_TO_SUBSCRIPTION]
    buffer_to_typed_ipb_events = event_data[constants.RCLCPP_BUFFER_TO_TYPED_IPB]
    _build_subscriptions(
        ret, rclcpp_events, rclcpp_cb_events, rcl_events, rmw_events, dds_events, ipb_to_subscription_events, buffer_to_typed_ipb_events,
    )

    timer_init_events = event_data[constants.RCL_TIMER_INIT]
    timer_link_node_events = event_data[constants.RCLCPP_TIMER_LINK_NODE]
    timer_link_callback_events = event_data[constants.RCLCPP_TIMER_CALLBACK_ADDED]
    _build_timers(
        ret, timer_init_events, timer_link_node_events, timer_link_callback_events
    )

    if process_callback_events:
        callback_start_events = event_data[constants.ROS_CALLBACK_START]
        callback_end_events = event_data[constants.ROS_CALLBACK_END]
        _build_callback_events(ret, callback_start_events, callback_end_events)

    if process_publish_events:
        rclcpp_publish_events = event_data[constants.RCLCPP_PUBLISH]
        rcl_publish_events = event_data[constants.RCL_PUBLISH]
        rmw_publish_events = event_data[constants.RMW_PUBLISH]
        dds_write_events = event_data[constants.DDS_WRITE]
        _build_publish_events(
            ret,
            rclcpp_publish_events,
            rcl_publish_events,
            rmw_publish_events,
            dds_write_events,
        )

        rclcpp_intra_publish_events = event_data[constants.RCLCPP_INTRA_PUBLISH]
        ring_buffer_enqueue_events = event_data[constants.RCLCPP_RINGBUFFER_ENQUEUE]
        _build_ip_publish_events(
            ret,
            rclcpp_intra_publish_events,
            ring_buffer_enqueue_events,
        )

    if process_subscription_events:
        rclcpp_take_events = event_data[constants.RCLCPP_TAKE]
        rcl_take_events = event_data[constants.RCL_TAKE]
        rmw_take_events = event_data[constants.RMW_TAKE]
        dds_read_events = event_data[constants.DDS_READ]
        _build_subscription_events(
            ret, rclcpp_take_events, rcl_take_events, rmw_take_events, dds_read_events
        )
        ring_buffer_dequeue_events = event_data[constants.RCLCPP_RINGBUFFER_DEQUEUE]
        _build_ip_subscription_events(
            ret, ring_buffer_dequeue_events
        )

    if process_callback_events and process_timer_events:
        _associate_timer_callbacks(ret)

    if process_callback_events and process_subscription_events:
        _associate_subscription_callbacks(ret)

    if process_publish_events and process_callback_events:
        _associate_subscription_event_to_publish_event(ret)

    if process_publish_events and process_callback_events and process_timer_events:
        _associate_publish_events_to_timer_callbacks(ret)

    if (
        process_publish_events
        and process_callback_events
        and process_subscription_events
    ):
        _associate_publish_events_to_subscription_callbacks(ret)
    return ret


def _build_contexts(graph: Graph, context_events: RawEvents) -> None:
    """
    Analyze event data for context initialization events
    """
    logger.debug(f"Building contexts from {len(context_events)} events")
    for event in context_events:
        graph.add_context(Context(event["context_handle"], event["version"]))
    logger.info(f"Detected {len(graph.contexts())} contexts")


def _build_nodes(graph: Graph, node_init_events: RawEvents) -> None:
    """
    Analyze event data for node initialization events
    """
    logger.debug(f"Building nodes from {len(node_init_events)} events")
    for event in node_init_events:
        node = Node(
            event["node_handle"],
            str(event["node_name"]),
            str(event["namespace"]),
            event["rmw_handle"],
        )
        graph.add_node(node)
    logger.info(f"Detected {len(graph.nodes)} nodes")


def _build_callbacks(graph: Graph, callback_events: RawEvents) -> None:
    logger.debug(f"Building callbacks from {len(callback_events)} register events")
    for event in callback_events:
        callback = Callback(
            event["callback"], str(event["symbol"]), int(event["_timestamp"])
        )
        graph.add_callback(callback)
    logger.info(f"Detected {len(graph.callbacks)} callbacks")


def _build_publishers(
    graph: Graph, rcl_events: RawEvents, rmw_events: RawEvents, dds_events: RawEvents
) -> None:
    debug_str = f"""Building publishers
    rcl events: {len(rcl_events)}
    rmw events: {len(rmw_events)}
    dds events: {len(dds_events)}"""
    logger.debug(debug_str)

    for event in rcl_events:
        pub = Publisher(
            publisher_handle=event["publisher_handle"],
            node_handle=event["node_handle"],
            rmw_publisher_handle=event["rmw_publisher_handle"],
            topic_name=event["topic_name"],
            queue_depth=event["queue_depth"],
        )

        pub.add_stamp("rcl_init_time", event["_timestamp"])

        if pub.handle in graph.nodes:
            node = graph.node_by_handle(pub.node_handle)
            if node:
                pub.node = node
        graph.add_publisher(pub)

    for event in rmw_events:
        found_pub = graph.publisher_by_rmw_handle(event["rmw_publisher_handle"])
        if found_pub is None:
            # logging.debug("Could not associate rmw publisher with publisher", event)
            continue
        found_pub.add_stamp("rmw_init_time", event["_timestamp"])
        found_pub.gid = [*event["gid"]][0:16]

    for event in dds_events:
        found_pub = graph.publisher_by_gid(event["gid"])
        if found_pub is None:
            # logging.debug(
            #    "Could not associate dds writer publisher with publisher", event
            # )
            continue

        found_pub.add_stamp("dds_init_time", event["_timestamp"])
        found_pub.dds_topic_name = event["topic_name"]
        found_pub.dds_writer = event["writer"]
    logger.info(f"Detected {len(graph.publishers)} publishers")


def _build_subscriptions(
    graph: Graph,
    rclcpp_events: RawEvents,
    rclcpp_cb_events: RawEvents,
    rcl_events: RawEvents,
    rmw_events: RawEvents,
    dds_events: RawEvents,
    ipb_to_subscription_events: RawEvents,
    buffer_to_typed_ipb_events: RawEvents,
) -> None:
    ss = f"""Building subscriptions
    rclcpp events: {len(rclcpp_events)}
    rclcpp callback events: {len(rclcpp_cb_events)}
    rcl events: {len(rcl_events)}
    rmw events: {len(rmw_events)}
    dds events: {len(dds_events)}"""
    logger.debug(ss)

    for event in rcl_events:
        sub = Subscription(
            subscription_handle=event["subscription_handle"],
            node_handle=event["node_handle"],
            rmw_subscription_handle=event["rmw_subscription_handle"],
            topic_name=event["topic_name"],
            queue_depth=event["queue_depth"],
        )
        sub.add_stamp("rcl_init_time", event["_timestamp"])
        graph.add_subscription(sub)

    for event in rclcpp_events:
        found_sub = graph.subscription_by_handle(event["subscription_handle"])
        if found_sub is None:
            continue
        if found_sub.reference:
            import copy
            old_sub = found_sub
            found_sub = copy.deepcopy(old_sub)
            graph.add_subscription(found_sub)
            found_sub._sibbling = old_sub
            old_sub._sibbling = found_sub

        found_sub.add_stamp("rclcpp_init_time", event["_timestamp"])
        found_sub.reference = event["subscription"]

    for event in rclcpp_cb_events:
        found_sub = graph.subscription_by_reference(event["subscription"])
        if found_sub is None:
            print("Could not associate rclcpp callback with subscription")
            continue
        found_sub.callback_handle = event["callback"]
        found_callback = graph.callback_by_handle(event["callback"])
        if found_callback:
            found_sub.callback = found_callback


    for event in rmw_events:
        found_sub = graph.subscription_by_rmw_handle(event["rmw_subscription_handle"])
        if found_sub is None:
            # logging.debug(
            #    "Could not associate rmw subscription with subscription", event
            # )
            continue

        found_sub.add_stamp("rmw_init_time", event["_timestamp"])
        found_sub.gid = [*event["gid"]][0:16]

    for event in dds_events:
        found_sub = graph.subscription_by_gid(event["gid"])
        if not found_sub:
            # logging.debug("Could not associate dds reader with subscription", event)
            continue

        found_sub.add_stamp("dds_init_time", event["_timestamp"])
        found_sub.dds_topic_name = event["topic_name"]
        found_sub.dds_reader_handle = event["reader"]

    for event in ipb_to_subscription_events:
        found_sub = graph.subscription_by_reference(event["subscription"])
        if found_sub is None:
            continue
        found_sub.ipb_handle = event["IPB"]

    for event in buffer_to_typed_ipb_events:
        found_sub = graph.subscription_by_ipb(event["IPB"])
        if found_sub is None:
            continue
        found_sub.buffer_handle = event['buffer']

    logger.info(f"Detected {len(graph.subscriptions)} subscriptions")


def _build_timers(
    graph: Graph,
    timer_init_events: RawEvents,
    rclcpp_timer_link_events: RawEvents,
    rclcpp_timer_callback_added_events: RawEvents,
) -> None:
    for event in rclcpp_timer_link_events:
        timer = Timer(event["timer_handle"], event["node_handle"])
        timer.add_stamp("rclcpp_init_time", event["_timestamp"])
        graph.add_timer(timer)

    for event in timer_init_events:
        found_timer = graph.timer_by_handle(event["timer_handle"])
        if not found_timer:
            continue
        found_timer.period = event["period"]
        found_timer.add_stamp("rcl_init_time", event["_timestamp"])

    for event in rclcpp_timer_callback_added_events:
        found_timer = graph.timer_by_handle(event["timer_handle"])
        if not found_timer:
            continue

        found_timer.callback_handle = event["callback"]
        found_callback = graph.callback_by_handle(found_timer.callback_handle)
        if found_callback:
            found_timer.callback = found_callback
            found_callback._source = found_timer


def _build_callback_events(
    graph: Graph, callback_start_events: RawEvents, callback_end_events: RawEvents
) -> None:
    events_by_callback = defaultdict(list)

    for event in callback_start_events:
        events_by_callback[event["callback"]].append(event)
    for event in callback_end_events:
        events_by_callback[event["callback"]].append(event)
    callback_events: List[CallbackEvent] = []

    for event_stream in events_by_callback.values():
        event_stream = sorted(event_stream, key=lambda x: (x["_timestamp"]))
        cur_event = None
        for entry in event_stream:
            if not cur_event:
                if entry["_name"] == constants.ROS_CALLBACK_START:
                    cur_event = CallbackEvent(
                        entry["callback"], entry["is_intra_process"]
                    )
                    cur_event._callback_start = entry["_timestamp"]
            else:
                if entry["_name"] == constants.ROS_CALLBACK_END:
                    cur_event._callback_end = entry["_timestamp"]
                    callback_events.append(cur_event)
                    cur_event = None

    for callback_event in callback_events:
        found_callback = graph.callback_by_handle(callback_event.callback_handle)
        if found_callback:
            found_callback.events().append(callback_event)
            callback_event._source = found_callback
        else:
            print("no callback found")

    for callback in graph._callbacks.values():
        callback._events.sort(key=lambda ev: ev._callback_start)


def _build_publish_events(
    graph: Graph,
    rclcpp_publish_events: RawEvents,
    rcl_publish_events: RawEvents,
    rmw_publish_events: RawEvents,
    dds_write_events: RawEvents,
):
    events_by_message = defaultdict(list)
    for event in rclcpp_publish_events:
        events_by_message[event["message"]].append(event)
    for event in rcl_publish_events:
        events_by_message[event["message"]].append(event)
    for event in rmw_publish_events:
        events_by_message[event["message"]].append(event)
    for event in dds_write_events:
        events_by_message[event["data"]].append(event)

    publish_events: List[PublishEvent] = []

    for event_stream in events_by_message.values():
        event_stream = sorted(event_stream, key=lambda x: (x["_timestamp"]))
        cur_event = None
        for entry in event_stream:
            if not cur_event:
                if entry["_name"] == constants.RCLCPP_PUBLISH:
                    cur_event = PublishEvent(entry["message"])
                    cur_event.add_stamp(constants.RCLCPP_PUBLISH, entry["_timestamp"])
            else:
                if entry["_name"] == constants.RCL_PUBLISH:
                    cur_event.add_stamp(constants.RCL_PUBLISH, entry["_timestamp"])
                    cur_event.publisher_handle = entry["publisher_handle"]
                elif entry["_name"] == constants.RMW_PUBLISH:
                    cur_event.add_stamp(constants.RMW_PUBLISH, entry["_timestamp"])
                elif entry["_name"] == constants.DDS_WRITE:
                    cur_event.add_stamp(constants.DDS_WRITE, entry["_timestamp"])
                    cur_event.add_stamp("timestamp", entry["timestamp"])
                    cur_event.dds_writer = entry["writer"]
                    publish_events.append(cur_event)
                    cur_event = None

    logger.info("Found %i publish events", len(publish_events))

    for pub_event in publish_events:
        found_publisher = graph.publisher_by_handle(pub_event.publisher_handle)
        if found_publisher:
            pub_event.source = found_publisher
            found_publisher.events.append(pub_event)

    for publisher in graph.publishers:
        publisher.events.sort(key=lambda ev: ev.timestamp())

def _build_ip_publish_events(
    graph: Graph,
    rclcpp_intra_publish_events: RawEvents,
    ring_buffer_enqueue_events: RawEvents,
):
    events_by_tid = defaultdict(list)
    for event in rclcpp_intra_publish_events:
        events_by_tid[event["vtid"]].append(event)
    for event in ring_buffer_enqueue_events:
        events_by_tid[event["vtid"]].append(event)

    publish_events: List[IPPublishEvent] = []

    for event_stream in events_by_tid.values():
        event_stream = sorted(event_stream, key=lambda x: (x["_timestamp"]))
        cur_event = None
        for entry in event_stream:
            if entry["_name"] == constants.RCLCPP_INTRA_PUBLISH:
                    if cur_event:
                        publish_events.append(cur_event)
                    cur_event = IPPublishEvent(entry["message"])
                    cur_event.publisher_handle = entry["publisher_handle"]
                    cur_event.add_stamp(constants.RCLCPP_INTRA_PUBLISH, entry["_timestamp"])
            elif entry["_name"] == constants.RINGBUFFER_ENQUEUE:
                    cur_event.add_stamp(constants.RINGBUFFER_ENQUEUE, entry["_timestamp"])
                    cur_event.add_message_in_buffer(entry["buffer"], entry["index"])

        if cur_event:
            publish_events.append(cur_event)


    logger.info("Found %i publish events", len(publish_events))

    for pub_event in publish_events:
        found_publisher = graph.publisher_by_handle(pub_event.publisher_handle)
        if found_publisher:
            pub_event.source = found_publisher
            found_publisher.events.append(pub_event)
            for mib in pub_event._messages_in_buffer:
              found_publisher.buffer_handles.add(mib.buffer)

    for publisher in graph.publishers:
        publisher.events.sort(key=lambda ev: ev.timestamp())

def _build_subscription_events(
    graph: Graph,
    rclcpp_take_events: RawEvents,
    rcl_take_events: RawEvents,
    rmw_take_events: RawEvents,
    dds_read_events: RawEvents,
):
    events = defaultdict(list)

    for event in rclcpp_take_events:
        events[event["message"]].append(event)
    for event in rcl_take_events:
        events[event["message"]].append(event)
    for event in rmw_take_events:
        events[event["message"]].append(event)
    for event in dds_read_events:
        events[event["buffer"]].append(event)

    read_events: List[SubscriptionEvent] = []

    for event_stream in events.values():
        event_stream = sorted(event_stream, key=lambda x: (x["_timestamp"]))
        cur_event = SubscriptionEvent()
        for entry in event_stream:
            if entry["_name"] in (constants.RCLCPP_TAKE, constants.RCL_TAKE):
                cur_event.add_stamp(entry["_name"], entry["_timestamp"])
            elif  entry["_name"] == constants.RMW_TAKE:
                cur_event.add_stamp(entry["_name"], entry["_timestamp"])
                cur_event.message_handle = entry["message"]
                cur_event.rmw_subscription_handle = entry["rmw_subscription_handle"]
                cur_event.source_timestamp = entry["source_timestamp"]
                cur_event.taken = entry["taken"]
            elif entry["_name"] == constants.DDS_READ:
                cur_event.add_stamp(constants.DDS_READ, entry["_timestamp"])
                cur_event.dds_reader = entry["reader"]

            if len(cur_event._stamps) == 4:
                read_events.append(cur_event)
                cur_event = SubscriptionEvent()

    logger.info("Found %i subscription events", len(read_events))

    subs_by_rmw = {}
    for sub in graph.subscriptions:
        subs_by_rmw[sub.rmw_handle] = sub

    for read_event in read_events:
        subs_by_rmw[read_event.rmw_subscription_handle].events.append(read_event)
        read_event.source = subs_by_rmw[read_event.rmw_subscription_handle]

    for subscription in graph.subscriptions:
        subscription.events.sort(key=lambda ev: ev.timestamp())

def _build_ip_subscription_events(
    graph: Graph,
    ring_buffer_dequeue_events: RawEvents,
):
    events = defaultdict(list)

    read_events: List[IpSubscriptionEvent] = []

    for entry in ring_buffer_dequeue_events:
        event = IpSubscriptionEvent(entry["buffer"], entry["index"])
        event.add_stamp(entry["_name"], entry["_timestamp"])
        read_events.append(event)


    subs_by_buffer = {}
    for sub in graph.subscriptions:
        subs_by_buffer[sub.buffer_handle] = sub

    for read_event in read_events:
        subs_by_buffer[read_event.buffer_handle].events.append(read_event)
        read_event.source = subs_by_buffer[read_event.buffer_handle]

    for subscription in graph.subscriptions:
        subscription.events.sort(key=lambda ev: ev.timestamp())

def _associate_subscription_callbacks(graph: Graph):
    for subscription in graph.subscriptions:
        sub_events = subscription.events
        sub_cb_events = subscription.callback.events()
        subscription.callback.source = subscription

        if len(sub_events) == 0:
            if subscription._sibbling and len(subscription._sibbling.events) == 0:
                print(f"No events for subscription: {subscription.name}")
            continue
        if len(sub_cb_events) == 0:
            if subscription._sibbling and len(subscription._sibbling.callback.events()) == 0:
                print(f"No callback events for subscription: {subscription.name}")
            continue

        for sub_event, callback_event in zip(sub_events, sub_cb_events):
            sub_event.callback = callback_event
            callback_event.trigger = sub_event
            sub_event.source = subscription
            callback_event.source = subscription


def _associate_timer_callbacks(graph: Graph):
    for timer in graph.timers():
        timer.callback.source = timer
        timer_cb_events = timer.callback.events()

        for timer_cb_event in timer_cb_events:
            timer_cb_event.source = timer
            timer_cb_event.trigger = timer


def _associate_subscription_event_to_publish_event(graph: Graph):
    def _associate(publisher: Publisher, subscription: Subscription):
        pubsub_events = []
        for event_idx, event in enumerate(subscription.events):
            if not isinstance(event, IpSubscriptionEvent):
                pubsub_events.append(
                {
                    "type": "subscription",
                    "event_idx": event_idx,
                    "timestamp": event.source_timestamp,
                }
            )
        for event_idx, event in enumerate(publisher.events):
            if not isinstance(event, IPPublishEvent):
                pubsub_events.append(
                    {
                        "type": "publication",
                        "event_idx": event_idx,
                        "timestamp": event._stamps["timestamp"],
                    }
                )

        pubsub_events = sorted(pubsub_events, key=lambda x: (x["timestamp"], x["type"]))

        cur_pub: Optional[Dict[str, Any]] = None
        for event in pubsub_events:
            if event["type"] == "publication":
                cur_pub = event
            elif event["type"] == "subscription":
                if cur_pub and event["timestamp"] == cur_pub["timestamp"]:
                    pub_event = publisher.events[cur_pub["event_idx"]]
                    sub_event = subscription.events[event["event_idx"]]
                    sub_event.trigger = pub_event
                else:
                    cur_pub = None

    def _associate_ip(publisher: Publisher, subscription: Subscription):
        pubsub_events_by_buffer = defaultdict(list)
        for event_idx, event in enumerate(subscription.events):
            if isinstance(event, IpSubscriptionEvent):
                pubsub_events_by_buffer[event.buffer_handle].append(
                    {
                        "type": "subscription",
                        "event_idx": event_idx,
                        "message_in_buffer" : MessageInBuffer(event.buffer_handle, event.index),
                        "timestamp": event.timestamp()
                    }
                )
        for event_idx, event in enumerate(publisher.events):
            if isinstance(event, IPPublishEvent):
                for event_in_buffer in event._messages_in_buffer:
                    pubsub_events_by_buffer[event_in_buffer._buffer_handle].append(
                        {
                            "type": "publication",
                            "event_idx": event_idx,
                            "message_in_buffer": event_in_buffer,
                            "timestamp": event.timestamp()
                        }
                    )

        for [k, pubsub_events] in pubsub_events_by_buffer.items():
            pubsub_events = sorted(pubsub_events, key=lambda x: (x["message_in_buffer"].index, x["timestamp"], x["type"]))

            cur_pub: Optional[Dict[str, Any]] = None
            for event in pubsub_events:
                if event["type"] == "publication":
                    cur_pub = event
                elif event["type"] == "subscription":
                    if not cur_pub or cur_pub["message_in_buffer"].index != event["message_in_buffer"].index:
                        continue
                    pub_event = publisher.events[cur_pub["event_idx"]]
                    sub_event = subscription.events[event["event_idx"]]
                    sub_event.trigger = pub_event
                    cur_pub = None

    for topic in graph.topics:
        if len(topic.subscriptions) == 0 or len(topic.publishers) == 0:
            continue
        for subscription in topic.subscriptions:
            if len(subscription.events) == 0:
                continue
            for publisher in topic.publishers:
                if len(publisher.events) == 0:
                    continue
                _associate(publisher, subscription)
                if subscription.buffer_handle in publisher.buffer_handles:
                    _associate_ip(publisher, subscription)

def _associate_publish_events_to_timer_callbacks(graph: Graph):
    for node in graph.nodes:
        for timer in node.timers:
            for publisher in node.publishers:
                _associate_publisher_to_callback(publisher, timer.callback)


def _associate_publish_events_to_subscription_callbacks(graph: Graph):
    for node in graph.nodes:
        for subscription in node.subscriptions:
            for publisher in node.publishers:
                _associate_publisher_to_callback(publisher, subscription.callback)

def _associate_publisher_to_callback(publisher: Publisher, callback: Callback):
    pub_idx = 0
    sub_idx = 0
    pub_events = publisher.events
    sub_events = callback.events()
    
    while pub_idx < len(pub_events) and sub_idx < len(sub_events):
        pub_event = pub_events[pub_idx]
        sub_event = sub_events[sub_idx]
        if pub_event.timestamp() < sub_event.start():
            pub_idx += 1
        elif pub_event.timestamp() > sub_event.end():
            sub_idx += 1
        else:
            pub_event.trigger = sub_event
            pub_idx += 1
