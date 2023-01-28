

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
