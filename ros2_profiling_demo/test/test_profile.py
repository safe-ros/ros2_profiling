def test_nodes(profile_data):
    assert len(profile_data.nodes()) == 20

    # Assert that all of the nodes under test are available
    # in the tracing data
    for node in profile_data.nodes():
        handle = profile_data.node_handle(node['name'])
        assert handle

def test_cpu(profile_data):
    containers = profile_data.containers()
    for container in containers:
        usage = profile_data.cpu_memory_usage(container)
        assert (usage['cpu_percent'] < 50).all()
