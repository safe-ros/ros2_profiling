from .callback import Callback, CallbackEvent
from .context import Context
from .node import Node
from .graph import Graph
from .publisher import Publisher, PublishEvent
from .subscription import Subscription, SubscriptionEvent
from .timer import Timer

from typing import List, Dict, Any

import pandas as pd

def build_graph(
        event_data: Dict[str, Any],
        callback_events: bool = True,
        publish_events: bool = True,
        subscription_events: bool = True,
        ) -> Graph:
    ret = Graph()

    _build_contexts(ret, event_data)
    _build_nodes(ret, event_data)
    _build_callbacks(ret, event_data)
    _build_publishers(ret, event_data)
    _build_subscriptions(ret, event_data)
    _build_timers(ret, event_data)

    if callback_events:
        _build_callback_events(ret, event_data)
    if publish_events:
        _build_publish_events(ret, event_data)
    if subscription_events:
        _build_subscription_events(ret, event_data)
    if callback_events and subscription_events:
        _associate_subscription_callbacks(ret, event_data)

    return ret

def _build_contexts(graph: Graph, event_data) -> None:
    for event in event_data['ros2:rcl_init']:
        graph.add_context(Context(event['context_handle'], event['version']))

def _build_nodes(graph: Graph, event_data) -> None:
    for event in event_data['ros2:rcl_node_init']:
        node = Node(event['node_handle'], str(event['node_name']),
            str(event['namespace']), event['rmw_handle'])
        graph.add_node(node)

def _build_callbacks(graph: Graph, event_data) -> None:
    for event in event_data['ros2:rclcpp_callback_register']:
        callback = Callback(event['callback'], str(event['symbol']))
        callback._rclcpp_init_time = event['_timestamp']
        graph.add_callback(callback)

def _build_publishers(graph: Graph, event_data) -> None:
    for event in event_data['ros2:rcl_publisher_init']:
        pub = Publisher(event['publisher_handle'])
        pub._rmw_handle = event['rmw_publisher_handle']
        pub._node_handle = event['node_handle']
        if pub._node_handle in graph._nodes:
            pub._node = graph._nodes[pub._node_handle]
        pub._topic_name = str(event['topic_name'])
        pub._queue_depth = event['queue_depth']
        pub._rcl_init_time = event['_timestamp']
        graph.add_publisher(pub)

    for event in event_data['ros2:rmw_publisher_init']:
        pub = None
        for p in graph._publishers.values():
            if p._rmw_handle == event['rmw_publisher_handle']:
                pub = p
                break
        if pub is None:
            # print("Could not associate rmw publisher with rcl publisher")
            continue
        pub._rmw_init_time = event['_timestamp']
        pub._gid = [*event['gid']][0:16]

    for event in event_data['dds:create_writer']:
        pub = None
        for p in graph._publishers.values():
            if p._gid == event['gid']:
                pub = p
                break
        if pub is None:
            # print(f"Could not associate dds writer: {event['topic_name']}")
            continue

        pub._dds_init_time = event['_timestamp']
        pub._dds_topic_name = event['topic_name']
        pub._dds_writer = event['writer']

def _build_subscriptions(graph: Graph, event_data) -> None:
    temp_subs = []
    for event in event_data['ros2:rclcpp_subscription_init']:
        sub = Subscription(event['subscription_handle'], event['subscription'])
        sub._rclcpp_init_time = event['_timestamp']
        temp_subs.append(sub)

    for event in event_data['ros2:rcl_subscription_init']:
        sub = None
        for s in temp_subs:
            if s._handle == event['subscription_handle']:
                sub = s
                break
        if sub is None:
            # print("Could not associate rcl subscription")
            continue

        sub._rmw_handle = event['rmw_subscription_handle']
        sub._rcl_init_time = event['_timestamp']
        sub._node_handle = event['node_handle']
        if sub._node_handle in graph._nodes:
            sub._node = graph._nodes[sub._node_handle]
        sub._topic_name = str(event['topic_name'])
        sub._queue_depth = event['queue_depth']

    for event in event_data['ros2:rclcpp_subscription_callback_added']:
        sub = None
        for s in temp_subs:
            if s._reference == event['subscription']:
                sub = s
                break
        if sub is None:
            # print("Could not associate subscription callback")
            continue

        sub._callback_handle = event['callback']

        if sub._callback_handle in graph._callbacks:
            sub._callback = graph._callbacks[sub._callback_handle]


    for event in event_data['ros2:rmw_subscription_init']:
        sub = None
        for s in temp_subs:
            if s._rmw_handle == event['rmw_subscription_handle']:
                sub = s
                break
        if sub is None:
            # print("Could not associate rmw subscription")
            continue

        sub._rmw_init_time = event['_timestamp']
        sub._gid = [*event['gid']][0:16]

    for event in event_data['dds:create_reader']:
        sub = None
        for s in temp_subs:
            if s._gid == event['gid']:
                sub = s
                break
        if not sub:
            # print(f"Could not associate dds reader: {event['topic_name']}")
            continue

        sub._dds_init_time = event['_timestamp']
        sub._dds_topic_name = event['topic_name']
        sub._dds_reader = event['reader']

    for sub in temp_subs:
        graph.add_subscription(sub)


def _build_timers(graph: Graph, event_data) -> None:
    temp_timers = []
    for event in event_data['ros2:rcl_timer_init']:
        t = Timer(event['timer_handle'])
        t._period = event['period']
        t._rcl_init_time = event['_timestamp']
        temp_timers.append(t)

    for event in event_data['ros2:rclcpp_timer_link_node']:
        timer = None
        for t in temp_timers:
            if t._handle == event['timer_handle']:
                timer = t
        if timer is None:
            continue

        timer._rclcpp_init_time = event['_timestamp']
        timer._node_handle = event['node_handle']
        if timer._node_handle in graph._nodes:
            timer._node = graph._nodes[timer._node_handle]

    for event in event_data['ros2:rclcpp_timer_callback_added']:
        timer = None
        for t in temp_timers:
            if t._handle == event['timer_handle']:
                timer = t
        if timer is None:
            continue

        timer._callback_handle = event['callback']

        if timer._callback_handle in graph._callbacks:
            timer._callback = graph._callbacks[timer._callback_handle]

    for timer in temp_timers:
        graph.add_timer(timer)

def _build_callback_events(graph: Graph, event_data) -> None:
    events = []
    for event in event_data['ros2:callback_start']:
        events.append({
            'event': 's',
            'is_intra_process': event['is_intra_process'],
            'timestamp': event['_timestamp'],
            'callback': event['callback'],
            'vpid': event['vpid'], 'vtid': event['vtid'], 'cpu_id': event['cpu_id']})
    for event in event_data['ros2:callback_end']:
        events.append({
            'event': 'e',
            'timestamp': event['_timestamp'],
            'callback': event['callback'],
            'vpid': event['vpid'], 'vtid': event['vtid'], 'cpu_id': event['cpu_id']})

    df = pd.DataFrame(events)
    df.sort_values(by=['callback','vpid', 'vtid', 'timestamp'], inplace=True)
    df.reset_index(drop=True, inplace=True)

    cur_event = None
    events = []
    for idx, row in df.iterrows():
        if row['event'] == 's':
            cur_event = CallbackEvent(row['callback'], row['is_intra_process'])
            cur_event._callback_start = row['timestamp']
            cur_event._vpid = row['vpid']
            cur_event._vtid = row['vtid']
            cur_event._cpu_id = row['cpu_id']
        elif cur_event and row['event'] == 'e':
            if (row['callback'] != cur_event._callback_handle or
                row['vpid'] != cur_event._vpid or
                row['vtid'] != cur_event._vtid):
                print('error associating: ', idx)
                cur_event=None
                break
            else:
                cur_event._callback_end = row['timestamp']
                events.append(cur_event)
                cur_event = None

    for event in events:
        if event.handle() in graph._callbacks:
            graph._callbacks[event.handle()]._events.append(event)
        else:
            # print("Could not associate CallbackEvent with Callback")
            pass

    for callback in graph._callbacks.values():
        callback._events.sort(key=lambda ev: ev._callback_start)

def _build_publish_events(graph: Graph, event_data):
    events = []

    for event in event_data['ros2:rclcpp_publish']:
        events.append({
            'event': 'rclcpp_publish',
            'timestamp': event['_timestamp'],
            'message': event['message'],
            'vpid': event['vpid'], 'vtid': event['vtid'], 'cpu_id': event['cpu_id']
        })

    for event in event_data['ros2:rcl_publish']:
        events.append({
            'event': 'rcl_publish',
            'timestamp': event['_timestamp'],
            'message': event['message'],
            'publisher_handle': event['publisher_handle'],
            'vpid': event['vpid'], 'vtid': event['vtid'], 'cpu_id': event['cpu_id']
        })

    for event in event_data['ros2:rmw_publish']:
        events.append({
            'event': 'rmw_publish',
            'timestamp': event['_timestamp'],
            'message': event['message'],
            'vpid': event['vpid'], 'vtid': event['vtid'], 'cpu_id': event['cpu_id']
        })

    for event in event_data['dds:write']:
        events.append({
            'event': 'dds_write',
            'timestamp': event['_timestamp'],
            'writer': event['writer'],
            'message': event['data'],
            'dds_timestamp': event['timestamp'],
            'vpid': event['vpid'], 'vtid': event['vtid'], 'cpu_id': event['cpu_id']
        })

    df = pd.DataFrame(events)
    df.sort_values(by=['message', 'vpid', 'vtid', 'timestamp'], inplace=True)
    df.reset_index(drop=True, inplace=True)
    df['used'] = False
    used_idx = df.columns.get_loc('used')

    print(f'Analyzing {len(df)} publish events, raw counts:')
    print(f'  rclcpp_publish: {len(event_data["ros2:rclcpp_publish"])}')
    print(f'  rcl_publish: {len(event_data["ros2:rcl_publish"])}')
    print(f'  rmw_publish: {len(event_data["ros2:rmw_publish"])}')
    print(f'  dds_write: {len(event_data["dds:write"])}')

    cur_event = None
    publish_events = []
    for idx, row in df.iterrows():
        if idx % 10000 == 0:
            print(f'Analyzed {idx} events')

        if row['event'] == 'rclcpp_publish':
            cur_event = PublishEvent(row['message'])
            cur_event._vpid = row['vpid']
            cur_event._vtid = row['vtid']
            cur_event._cpu_id = row['cpu_id']
            cur_event._rclcpp_init_time = row['timestamp']
            df.iloc[idx, used_idx] = True
        elif cur_event and row['event'] == 'rcl_publish':
            if (row['message'] != cur_event._message_handle or
                row['vpid'] != cur_event._vpid or
                row['vtid'] != cur_event._vtid):
                continue
            cur_event._rcl_init_time = row['timestamp']
            cur_event._publisher_handle = row['publisher_handle']
            df.iloc[idx, used_idx] = True
        elif cur_event and row['event'] == 'rmw_publish':
            if (row['message'] != cur_event._message_handle or
                row['vpid'] != cur_event._vpid or
                row['vtid'] != cur_event._vtid):
                continue
            cur_event._rmw_init_time = row['timestamp']
            df.iloc[idx, used_idx] = True
        elif cur_event and row['event'] == 'dds_write':
            if (row['message'] != cur_event._message_handle or
                row['vpid'] != cur_event._vpid or
                row['vtid'] != cur_event._vtid):
                continue
            cur_event._dds_init_time = row['timestamp']
            cur_event._dds_writer = row['writer']
            cur_event._dds_timestamp = row['dds_timestamp']

            df.iloc[idx, used_idx] = True
            publish_events.append(cur_event)
            cur_event = None

    rclcpp_events_found = len(publish_events)
    print(f'Found {rclcpp_events_found} complete rclcpp_publish events')

    df2 = df[~df['used']].copy()
    df2.reset_index(drop=True, inplace=True)

    print(f'Evaluating {len(df2)} remaining events')

    cur_event = None
    for idx, row in df2.iterrows():
        if row['event'] == 'rcl_publish':
            cur_event = PublishEvent(row['message'])
            cur_event._vpid = row['vpid']
            cur_event._vtid = row['vtid']
            cur_event._cpu_id = row['cpu_id']
            cur_event._rcl_init_time = row['timestamp']
            cur_event._publisher_handle = row['publisher_handle']
            df2.iloc[idx, used_idx] = True
        elif cur_event and row['event'] == 'rmw_publish':
            if (row['message'] != cur_event._message_handle or
                row['vpid'] != cur_event._vpid or
                row['vtid'] != cur_event._vtid):
                continue
            cur_event._rmw_init_time = row['timestamp']
            df2.iloc[idx, used_idx] = True

        elif cur_event and row['event'] == 'dds_write':
            if (row['message'] != cur_event._message_handle or
                row['vpid'] != cur_event._vpid or
                row['vtid'] != cur_event._vtid):
                continue
            cur_event._dds_init_time = row['timestamp']
            cur_event._dds_writer = row['writer']
            df2.iloc[idx, used_idx] = True
            publish_events.append(cur_event)
            cur_event = None
    rcl_events_found = len(publish_events) - rclcpp_events_found
    print(f'Found {rcl_events_found} additional rcl_publish only events')

    for event in publish_events:
        if event._publisher_handle in graph._publishers:
            graph._publishers[event._publisher_handle]._events.append(event)

    for publisher in graph._publishers.values():
        publisher._events.sort(key=lambda ev: ev._rcl_init_time)

def _build_subscription_events(graph: Graph, event_data):
    events = []

    for event in event_data['ros2:rclcpp_take']:
        events.append({
            'event': 'rclcpp_take',
            'timestamp': event['_timestamp'],
            'message': event['message'],
            'vpid': event['vpid'], 'vtid': event['vtid'], 'cpu_id': event['cpu_id']
        })
    for event in event_data['ros2:rcl_take']:
        events.append({
            'event': 'rcl_take',
            'timestamp': event['_timestamp'],
            'message': event['message'],
            'vpid': event['vpid'], 'vtid': event['vtid'], 'cpu_id': event['cpu_id']
        })
    for event in event_data['ros2:rmw_take']:
        events.append({
            'event': 'rmw_take',
            'timestamp': event['_timestamp'],
            'message': event['message'],
            'rmw_subscription_handle': event['rmw_subscription_handle'],
            'source_timestamp': event['source_timestamp'],
            'taken': event['taken'],
            'vpid': event['vpid'], 'vtid': event['vtid'], 'cpu_id': event['cpu_id']
        })
    for event in event_data['dds:read']:
        events.append({
            'event': 'dds_read',
            'timestamp': event['_timestamp'],
            'message': event['buffer'],
            'reader': event['reader'],
            'vpid': event['vpid'], 'vtid': event['vtid'], 'cpu_id': event['cpu_id']
        })

    df = pd.DataFrame(events)
    df.sort_values(by=['vpid', 'vtid', 'timestamp'], inplace=True, ascending=False)
    df.reset_index(drop=True, inplace=True)

    cur_event = None
    subscribe_events = []
    for idx, row in df.iterrows():
        if row['event'] == 'rclcpp_take':
            cur_event = SubscriptionEvent(row['message'])
            cur_event._vpid = row['vpid']
            cur_event._vtid = row['vtid']
            cur_event._cpu_id = row['cpu_id']
            cur_event._rclcpp_init_time = row['timestamp']
        elif cur_event and row['event'] == 'rcl_take':
            if (row['message'] != cur_event._message_handle):
                continue
            cur_event._rcl_init_time = row['timestamp']
        elif cur_event and row['event'] == 'rmw_take':
            if (row['message'] != cur_event._message_handle):
                continue
            cur_event._rmw_init_time = row['timestamp']
            cur_event._rmw_subscription_handle = int(row['rmw_subscription_handle'])
        elif cur_event and row['event'] == 'dds_read':
            if (row['message'] != cur_event._message_handle):
                continue
            cur_event._dds_init_time = row['timestamp']
            cur_event._dds_reader = int(row['reader'])
            subscribe_events.append(cur_event)
            cur_event = None

    print(f'Found {len(subscribe_events)} subscription events')

    subs_by_rmw = {}
    for sub in graph._subscriptions.values():
        subs_by_rmw[sub._rmw_handle] = sub

    for event in subscribe_events:
        subs_by_rmw[event._rmw_subscription_handle]._events.append(event)

    for subscription in graph._subscriptions.values():
        subscription._events.sort(key=lambda ev: ev._rcl_init_time)

def _associate_subscription_callbacks(graph: Graph, event_data):
    for subscription in graph._subscriptions.values():
        sub_events = subscription.events()
        sub_cb_events = subscription.callback().events()

        if len(sub_events) == 0:
            print(f"No events for subscription: {subscription.topic_name()}")
            continue
        if len(sub_cb_events) == 0:
            print(f"No callback events for subscription: {subscription.topic_name()}")
            continue

        if len(sub_events) != len(sub_cb_events):
            print(f"Mismatch in event numbers for : {subscription.topic_name()}")
            print(f" Subscription Events: {len(sub_events)}")
            print(f" Callback Events: {len(sub_cb_events)}")

        for (sub_event, callback_event) in zip(sub_events, sub_cb_events):
            sub_event._callback = callback_event
            callback_event._trigger = sub_event


def _associate_pubsub(graph: Graph, event_data):
    for topic in graph.topics():
        events = []
        if len(topic.subscriptions()) == 0 or len(topic.publishers()) == 0:
            continue

        for sub_idx, sub in enumerate(topic.subscriptions()):
            for event_idx, ev in enumerate(sub.events()):
                events.append({'type': 'sub',
                               'topic_num': int(sub_idx),
                               'event_num': int(event_idx),
                               'ts': ev._dds_init_time})
        for pub_idx, pub in enumerate(topic.publishers()):
            for event_idx, ev in enumerate(pub.events()):
                events.append({'type': 'pub',
                               'topic_num': int(pub_idx),
                               'event_num': int(event_idx),
                               'ts': ev._dds_init_time})
        if len(events) == 0:
            continue

        df = pd.DataFrame(events)
        df.sort_values(by=['ts'], inplace=True, ascending=False)

        cur_event = None
        for idx, row in df.iterrows():
            if row['type'] == 'sub':
                cur_sub = topic.subscriptions()[row['topic_num']]
                cur_event = cur_sub.events()[row['event_num']]
            elif cur_event and row['type'] == 'pub':
                cur_event._trigger = topic.publishers()[row['topic_num']].events()[row['event_num']]
                cur_event = None
