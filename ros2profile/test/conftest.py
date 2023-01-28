import pytest

from ros2profile.api.process import load_mcap_data, load_event_graph

def pytest_addoption(parser):
    parser.addoption("--input-dir", action="store")


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
    return load_mcap_data(input_dir)

@pytest.fixture(scope='session')
def profile_event_graph(request):
    input_dir = request.config.option.input_dir
    if input_dir is None:
        pytest.skip()
    return load_event_graph(input_dir)

