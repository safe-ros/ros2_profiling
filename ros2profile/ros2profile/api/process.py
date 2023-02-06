# Copyright 2023 Open Source Robotics Foundation
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

import glob
import os
import pickle

import mcap_ros2.reader

import pandas as pd

from ros2profile.data.convert.ctf import load_ctf
from ros2profile.data import build_graph

def process_memory_state(msg):
    return {
        '_log_time': msg.log_time,
        'total_program_size': msg.ros_msg.total_program_size,
        'resident_size': msg.ros_msg.resident_size,
        'shared_page_count': msg.ros_msg.shared_page_count,
        'text_size': msg.ros_msg.text_size,
        'lib_size': msg.ros_msg.lib_size,
        'data_size': msg.ros_msg.data_size,
        'dirty_pages': msg.ros_msg.dirty_pages
    }

def process_io_stats(msg):
    return {
        '_log_time': msg.log_time,
        'bytes_read': msg.ros_msg.bytes_read,
        'bytes_written': msg.ros_msg.bytes_written,
        'characters_read': msg.ros_msg.characters_read,
        'characters_written': msg.ros_msg.characters_written,
        'read_syscalls': msg.ros_msg.read_syscalls,
        'write_syscalls': msg.ros_msg.write_syscalls,
        'cancelled_byte_writes': msg.ros_msg.cancelled_byte_writes
    }

def process_stat(msg):
    return {
        '_log_time': msg.log_time,
    }

def process_cpu_memory_usage(msg):
    return {
        '_log_time': msg.log_time,
        'pid': msg.ros_msg.pid,
        'elapsed_time': msg.ros_msg.cpu_usage.elapsed_time,
        'user_mode_time': msg.ros_msg.cpu_usage.user_mode_time,
        'total_user_mode_time': msg.ros_msg.cpu_usage.total_user_mode_time,
        'kernel_model_time': msg.ros_msg.cpu_usage.kernel_mode_time,
        'total_kernel_mode_time': msg.ros_msg.cpu_usage.total_kernel_mode_time,
        'cpu_percent': msg.ros_msg.cpu_usage.percent,
        'load_avg_1min': msg.ros_msg.cpu_usage.load_average.last_1min,
        'load_avg_5min': msg.ros_msg.cpu_usage.load_average.last_5min,
        'load_avg_15min': msg.ros_msg.cpu_usage.load_average.last_15min,
        'task_counts': msg.ros_msg.cpu_usage.load_average.task_counts,
        'available_tasks': msg.ros_msg.cpu_usage.load_average.available_tasks,
        'last_created_task': msg.ros_msg.cpu_usage.load_average.last_created_task,


        'max_resident_set_size': msg.ros_msg.memory_usage.max_resident_set_size,
        'shared_size': msg.ros_msg.memory_usage.shared_size,
        'virtual_size': msg.ros_msg.memory_usage.virtual_size,
        'memory_percent': msg.ros_msg.memory_usage.percent
    }


PROCESSORS = {
    'topnode_interfaces/msg/MemoryState': process_memory_state,
    'topnode_interfaces/msg/IoStats': process_io_stats,
    'topnode_interfaces/msg/CpuMemoryUsage': process_cpu_memory_usage,
    'topnode_interfaces/msg/Stat': process_stat
}

def process_one(input_file):
    data = {}

    for msg in mcap_ros2.reader.read_ros2_messages(input_file):
        schema = msg.schema.name
        topic = msg.channel.topic

        if topic not in data:
            data[topic] = []

        if schema in PROCESSORS:
            data[topic].append(PROCESSORS[schema](msg))

    for (topic, values) in data.items():
        data[topic] = pd.DataFrame.from_dict(values)

    return data


def process(input_path):
    mcap_files = glob.glob(input_path + '*.mcap')
    print(f'Processing {len(mcap_files)} topnode files')

    for mcap_file in mcap_files:
        base = os.path.splitext(mcap_file)[0]
        data = process_one(mcap_file)

        with open(base + '.converted', 'wb') as f:
            p = pickle.Pickler(f, protocol=4)
            p.dump(data)

    events = load_ctf(input_path)
    graph = build_graph(events)

    with open(os.path.join(input_path, 'event_graph'), 'wb') as f:
        p = pickle.Pickler(f, protocol=4)
        p.dump(graph)


def load_mcap_data(input_path):
    # Find candidate files
    mcap_files = glob.glob(input_path + '*.mcap')
    data = {}
    for mcap_file in mcap_files:
        base = os.path.splitext(mcap_file)[0]

        if os.path.exists(base + '.converted'):
            with open(base + '.converted', 'rb') as f:
                p = pickle.Unpickler(f)
                mcap_data = p.load()
            data[os.path.basename(base)] = mcap_data
    return data

def load_event_graph(input_path):
    if not os.path.exists(os.path.join(input_path, 'event_graph')):
        process(input_path)

    with open(os.path.join(input_path, 'event_graph'), 'rb') as f:
        p = pickle.Unpickler(f)
        graph_data = p.load()
    return graph_data
