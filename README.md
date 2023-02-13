# ros2_profiling

A set of tools and techniques for evaluating performance of ROS 2 based systems

## Goals

* Provide a tool for launching arbitrary ROS 2 systems instrumented for important performance metrics:
  * System Metrics
    * CPU Usage
    * Memory Usage
    * IO Statistics
  * Instrumentation Points
    * Callback durations
    * Message latency/jitter
* Provide tooling for analyzing the results of the launched system
  * Via pytest-style assertings
  * Via plots or tool-based introspection
* Minimize the load on the system under test

## Methodology

In order to minimize the system load, it was decided to use efficient formats for real-time collection and defer a majority of the processing to after the execution of the test.
As a result, the implementation can be considered in three phases:
* Collection: efficiently recording instrumented data
* Post-processing: expanding the recorded formats into a more easy-to-use format
* Analysis: Perform testing/assertions on available data as well as more detailed interactive exploration.

### Collection

Selected data is collected from a specified system-under-test.
To collection system-wide metrics, we utilize the [topnode](https://github.com/safe-ros/topnode), a component node that will instrument the parent container to track various information available through `/proc` endpoints.
In practice, the data available from `topnode` largely mirrors what would be retrieved via `top`.

In addition to system-wide metrics, individual metrics are derived from [ros2_tracing](https://github.com/ros2/ros2_tracing) instrumentation points.
`ros2_tracing` adds instrumentation points across the ROS 2 stack from the DDS layer up through the rclcpp client library.
As these instrumentation points are reached, the relevant information is recorded in a performant manner to be analyzed after execution.

In order to accurately connect metrics across nodes, this also makes use of the message flow instrumentation points that are currently in development.
These additional trace points and their use are described in [Message Flow Analysis with Complex Causal Links for Distributed ROS 2 Systems](https://arxiv.org/abs/2204.10208).

### Post-processing


### Analysis

## Usage

### Installation

#### Setup LTTng and ros2_tracing

Since `ros2_tracing` depends on LTTng, we must first install that:

```
sudo apt-get update
sudo apt-get install lttng-tools liblttng-ust-dev
sudo apt-get install python3-babeltrace python3-lttng

# Also install lttng kernel tracing for additional memory/cpu/threading informatoin
sudo apt-get install lttng-modules-dkms
```

Additionally, if you're using kernel tracing with a non-root user, make sure that the tracing group exists and that your user is added to it.

```
# Create group if it doesn't exist
sudo groupadd -r tracing
# Add user to the group
sudo usermod -aG tracing $USER
```

#### Note for Ubuntu 22.04

LTTng-UST is not built with SDT support in the package repositories.
Since message flow analysis makes use of SDT support, it is necessary to build a custom copy of lttng-ust

```
sudo apt install systemtap-sdt-dev
git clone https://github.com/lttng/lttng-ust -b stable-2.13
cd lttng-ust
./bootstrap
./configure --with-sdt
make && make install
```

#### Building the workspace

With lttng setup, we can create and build a workspace to use the reference system 

```
# Create Workspace
mkdir -p ~/safe_ros/src
cd ~/safe_ros

# Download and import repos file
wget https://raw.githubusercontent.com/safe-ros/ros2_profiling/main/ros2_profiling_demo/demo.repos
vcs import src < demo.repos 
rosdep install --from-paths src --ignore-src -r -y
```


```
# Build the demo workspace
cd ~/safe_ros
colcon build 
```

Once the build is finished, activate the workspace (repeat in each newly-opened terminal).

```
source ~/safe_ros/install/setup.sh
```

### Profiling the demonstration system

Once the installation is complete, we can profile the demonstration [reference_system](https://github.com/safe-ros/reference_system).

First verify that tracing is set up correctly and enabled:
```
$ ros2 run tracetools status
Tracing enabled
```

Then launch the demonstration system with the specified configuration:


```
ros2 profile launch \
  --launch-file ./src/reference_system/launch/reference_system.launch.py \
  --config-file  ./src/ros2_profiling/ros2_profiling_demo/config/reference_system.yaml
```

The `topnode` uses ROS 2 lifecycle states to determine when to start/stop recording, so we can begin the recording via:

```
ros2 lifecycle set reference_system_control_monitor configure
ros2 lifecycle set reference_system_robot_monitor configure

ros2 lifecycle set reference_system_control_monitor activate 
ros2 lifecycle set reference_system_robot_monitor activate 
```

Once the end of the recording session is reached, either the launch can be terminated with `Ctrl-C` or the recording nodes can be shut down via:

```
ros2 lifecycle set reference_system_control_monitor deactivate
ros2 lifecycle set reference_system_robot_monitor deactivate 

ros2 lifecycle set reference_system_control_monitor shutdown
ros2 lifecycle set reference_system_robot_monitor shutdown
```

Once the session is done, recording can be verified via:

```
ls ~/.ros/profile/
```

There should be an entry corresponding to the recording made.

### Post-processing results


Post process the results into something usable by the test suite

```
ros2 profile process ~/.ros/profile/reference_system-20230117095738/
```

### Asserting demonstration system results 

Run a set of unit tests to assert performance of the system under test

```
ros2 profile run_test ~/.ros/profile/reference_system-20230117104350/ ./src/ros2_profiling/ros2_profiling_demo/test/test_profile.py
````

### Other analysis

