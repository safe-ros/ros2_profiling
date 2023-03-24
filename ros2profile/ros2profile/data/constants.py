# Copyright 2023 Open Source Robotics Foundation, Inc.
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

RCL_INIT = 'ros2:rcl_init'
RCL_NODE_INIT = 'ros2:rcl_node_init'
RCL_PUBLISHER_INIT = 'ros2:rcl_publisher_init'
RCL_SUBSCRIPTION_INIT = 'ros2:rcl_subscription_init'

RMW_PUBLISHER_INIT = 'ros2:rmw_publisher_init'
RMW_SUBSCRIPTION_INIT = 'ros2:rmw_subscription_init'

RCLCPP_CALLBACK_REGISTER = 'ros2:rclcpp_callback_register'
RCLCPP_SUBSCRIPTION_INIT = 'ros2:rclcpp_subscription_init'
RCLCPP_SUBSCRIPTION_CALLBACK_ADDED = 'ros2:rclcpp_subscription_callback_added'

DDS_CREATE_READER = 'dds:create_reader'
DDS_CREATE_WRITER = 'dds:create_writer'

RCL_TIMER_INIT = 'ros2:rcl_timer_init'
RCLCPP_TIMER_LINK_NODE = 'ros2:rclcpp_timer_link_node'
RCLCPP_TIMER_CALLBACK_ADDED = 'ros2:rclcpp_timer_callback_added'

ROS_CALLBACK_START = 'ros2:callback_start'
ROS_CALLBACK_END = 'ros2:callback_end'

RCLCPP_PUBLISH = 'ros2:rclcpp_publish'
RCL_PUBLISH = 'ros2:rcl_publish'
RMW_PUBLISH = 'ros2:rmw_publish'
DDS_WRITE = 'dds:write'

RCLCPP_TAKE = 'ros2:rclcpp_take'
RCL_TAKE = 'ros2:rcl_take'
RMW_TAKE = 'ros2:rmw_take'
DDS_READ = 'dds:read'

RCLCPP_IPB_TO_SUBSCRIPTION = 'ros2:rclcpp_ipb_to_subscription'
RCLCPP_BUFFER_TO_TYPED_IPB = 'ros2:rclcpp_buffer_to_ipb'
RCLCPP_CONSTRUCT_RINGBUFFER = 'ros2:rclcpp_construct_ring_buffer'
RCLCPP_RINGBUFFER_ENQUEUE = 'ros2:rclcpp_ring_buffer_enqueue'
RCLCPP_RINGBUFFER_DEQUEUE = 'ros2:rclcpp_ring_buffer_dequeue'
RCLCPP_RINGBUFFER_CLEAR = 'ros2:rclcpp_ring_buffer_clear'
RCLCPP_INTRA_PUBLISH = 'ros2:rclcpp_intra_publish'

