import pytest

import os
import yaml

from ros2profile.api.process import load_files, load_trace

def pytest_addoption(parser):
    parser.addoption("--input-dir", action="store")


class ProfileDataModel():
    def __init__(self, input_dir):
        self.input_dir = input_dir

        with open(os.path.join(input_dir, 'config.yaml'), 'r') as f:
            self.config = yaml.load(f, Loader=yaml.SafeLoader)
        self.trace_data = load_trace(input_dir)
        self.mcap_data = load_files(input_dir)

    def containers(self):
        return self.config['containers']

    def nodes(self):
        return self.config['nodes']

    def node_handle(self, node_name):
        return self.trace_data.data.nodes[
            self.trace_data.data.nodes.name == node_name
        ].to_dict()

    def cpu_memory_usage(self, container):
        return self.mcap_data[container]['~/cpu_memory_usage']


@pytest.fixture(scope='session')
def input_dir(request):
    input_dir = request.config.option.input_dir
    if input_dir is None:
        pytest.skip()
    return input_dir

@pytest.fixture(scope='session')
def profile_data(request):
    input_dir = request.config.option.input_dir
    if input_dir is None:
        pytest.skip()
    return ProfileDataModel(input_dir)
