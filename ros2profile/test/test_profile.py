

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
        usage = profile_data.cpu_memory_usage(container['name'])
        assert (usage['cpu_percent'] < 50).all()


def test_memory_usage(profile_data):
    containers = profile_data.containers()
    for container in containers:
        usage = profile_data.cpu_memory_usage(container['name'])
        assert (usage['memory_percent'] < 0.01).all()

        assert(usage['memory_percent'].median() < 1.0)


def test_callback_durations(profile_data):
    callbacks = []
    durations = []

    trace = profile_data.trace_data

    callback_symbols = trace.get_callback_symbols()
    for obj, symbol in callback_symbols.items():

        reference = trace.data.callback_objects.loc[
                    trace.data.callback_objects['callback_object'] == obj
                ].index.values.astype(int)[0]

        if reference in trace.data.timers.index:
            type_name = 'Timer'
            info = trace.get_timer_handle_info(reference)
        elif reference in trace.data.rcl_publishers.index:
            type_name = 'Publisher'
            info = trace.get_publisher_handle_info(reference)
        elif reference in trace.data.subscription_objects.index:
            type_name = 'Subscription'
            info = trace.get_subscription_reference_info(reference)
        elif reference in trace.data.services.index:
            type_name = 'Service'
            info = trace.get_service_handle_info(reference)
        elif reference in trace.data.clients.index:
            type_name = 'Client'
            info = trace.get_client_handle_info(reference)

        if 'topic' in info and info['topic'] == '/parameter_events':
            continue

        info['symbol'] = symbol

        duration_df = trace.get_callback_durations(obj)
        callbacks.append((info, duration_df))


    for (callback, duration_df) in callbacks:
        if callback['node'] == 'georgetown':
            print(callback['node'],
            assert (duration_df['duration'].mean().microseconds < 2e3)
