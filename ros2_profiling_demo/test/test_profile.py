import numpy as np

def check_diff(field, tol=1e-6):
    check = np.abs(field.max() - field.min())

    if check >= tol:
        print(field.max(), field.min())
    return check < tol

def test_reference_system_control(profile_data):
    '''
    Demonstrate asserting based on topnode-collected profiling data
    '''
    data = None
    for key in profile_data.keys():
        if key.find('reference_system_control') >= 0:
            data = profile_data[key]
    assert data is not None

    # By default:
    # Topnode data should have 4 message types:
    assert '~/cpu_memory_usage' in data
    assert '~/memory_state' in data
    assert '~/io_stats' in data
    assert '~/stat' in data

    cpu_memory_usage = data['~/cpu_memory_usage']
    memory_state = data['~/memory_state']
    io_stats = data['~/io_stats']
    stat = data['~/stat']

    # CPU should never exceed 5%
    assert np.all(cpu_memory_usage['cpu_percent'] < 5)

    # Memory usage should stay constant
    assert check_diff(cpu_memory_usage.max_resident_set_size)
    assert check_diff(cpu_memory_usage.shared_size)
    assert check_diff(cpu_memory_usage.virtual_size)
    assert check_diff(cpu_memory_usage.memory_percent)
    assert check_diff(memory_state.resident_size, 100)


def test_reference_system_robot(profile_data):
    data = None
    for key in profile_data.keys():
        if key.find('reference_system_control') >= 0:
            data = profile_data[key]
    assert data is not None

    # By default:
    # Topnode data should have 4 message types:
    assert '~/cpu_memory_usage' in data
    assert '~/memory_state' in data
    assert '~/io_stats' in data
    assert '~/stat' in data

    cpu_memory_usage = data['~/cpu_memory_usage']
    memory_state = data['~/memory_state']
    io_stats = data['~/io_stats']
    stat = data['~/stat']

    # CPU should never exceed 5%
    assert np.all(cpu_memory_usage['cpu_percent'] < 5)

    # Memory usage should stay constant
    assert check_diff(cpu_memory_usage.max_resident_set_size)
    assert check_diff(cpu_memory_usage.shared_size)
    assert check_diff(cpu_memory_usage.virtual_size)
    assert check_diff(cpu_memory_usage.memory_percent)
    assert check_diff(memory_state.resident_size, 100)
