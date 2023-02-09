import numpy as np

from ros2profile.data.event_sequence import EventSequence

def test_sequence(profile_event_graph):
    graph = profile_event_graph
    nodes = graph.nodes('arequipa')
    assert len(nodes) == 1
    arequipa = nodes[0]

    subs = arequipa.subscriptions()
    assert len(subs) == 1

    arkansas_sub = subs[0]

    sub_events = arkansas_sub.callback().events()
    assert len(sub_events) > 0

    events = []
    for event in sub_events:
        events.append(EventSequence(event))

    # We are expecting 26 events in the chain
    # Depending on which tracepoints are available
    assert len(events[0].sequence) < 30

    latencies = [e.latency() for e in events]

    # Normalize to seconds
    latencies = np.array(latencies)/1e9

    # Assert mean latency is less than 1 ms
    assert np.mean(latencies) < 1e-3

    # Assert jitter is less than 100 microseconds
    assert np.std(latencies) < 1e-4

    # Assert max latency is less than 1 ms
    assert np.max(latencies) < 1e-3

    # Assert median latency is less than 1 ms
    assert np.median(latencies) < 1e-3
