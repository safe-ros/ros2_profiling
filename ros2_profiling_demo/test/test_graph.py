import numpy as np

def test_graph(profile_event_graph):
    graph = profile_event_graph
    assert len(graph.nodes()) == 31
    assert len(graph.topics()) == 29
    assert len(graph.publishers()) == 29
    assert len(graph.subscriptions()) == 36


def test_graph_hamburg(profile_event_graph):
    graph = profile_event_graph

    # Retrieve a node by name
    matching_nodes = profile_event_graph.nodes('hamburg')
    assert len(matching_nodes) == 1
    hamburg = matching_nodes[0]

    # Check node publishers and subscriptions
    assert len(hamburg.timers()) == 0
    assert len(hamburg.publishers()) == 1
    assert len(hamburg.subscriptions()) == 4

    # Evaluate each subscriptions' callback duration
    for sub in hamburg.subscriptions():
        durations = [e.duration() for e in sub.callback().events()]
        assert np.mean(durations) < 1e5  # ns
        assert np.std(durations) < 1e5  # ns

    pub = hamburg.publishers()[0]
    events = np.array([ev._rclcpp_init_time for ev in pub.events()])

    pub_deltas = np.diff(events) / 1e9
    period = np.mean(pub_deltas)
    stddev = np.std(pub_deltas)

    # Period should be every 200 ms
    # Assert mean within 1 microsecond
    # Assert std within 1 millisecond
    assert np.abs(period - 0.2) < 1e-6
    assert np.abs(period - 0.2) < 1e-6
    assert stddev < 1e-3
