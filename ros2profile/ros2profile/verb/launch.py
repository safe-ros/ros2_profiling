
import os
import shutil
import yaml

from typing import Optional

from ros2profile.verb import VerbExtension

import launch
import launch.event_handlers
from launch.some_actions_type import SomeActionsType
import launch_ros.actions

from tracetools_launch.action import Trace
from tracetools_trace.tools import path


class LaunchVerb(VerbExtension):
    def add_arguments(self, parser, cli_name):  #noqa: D102
        parser.add_argument(
            '--launch-file', help='Launch file containing description of system under test'
        )
        parser.add_argument(
            '--config-file', help='Profiling configuration file'
        )

    def main(self, *, args):
        if not os.path.exists(args.config_file):
            print(f"Config file does not exist: {args.config_file}")
            return

        config = None
        with open(args.config_file, 'r', encoding='utf8') as f:
            config = yaml.load(f, Loader=yaml.SafeLoader)

        if not config:
            print(f"Failed to load config: {args.config_file}")
            return

        launch_description = launch.LaunchDescription([
            launch.actions.IncludeLaunchDescription(
                launch.launch_description_sources.AnyLaunchDescriptionSource(
                    args.launch_file
                ),
            ),
        ])

        session_name = 'ros2profile-tracing-session'
        base_path = '~/.ros/profile'
        append_timestamp = False

        context_fields = {
            'kernel': ['vpid', 'vtid', 'procname'],
            'userspace': ['vpid', 'vtid', 'procname'],
        }

        events_kernel = []
        events_ust = ['dds:*', 'ros2:*']

        if 'record_path' in config:
            base_path = config['record_path']

        if 'tracing' in config:
            trace_config = config['tracing']
            if 'session_name' in trace_config:
                session_name = trace_config['session_name']

            if 'kernel' in trace_config:
                if 'events' in trace_config['kernel']:
                    events_kernel = trace_config['kernel']['events']
                if 'context_field' in trace_config['kernel']:
                    context_fields['kernel'] = trace_config['kernel']['context_fields']

            if 'ust' in trace_config:
                if 'events' in trace_config['ust']:
                    events_ust = trace_config['ust']['events']
                if 'context_field' in trace_config['ust']:
                    context_fields['userspace'] = trace_config['ust']['context_fields']

        if len(events_kernel) == 0:
            del context_fields['kernel']
        if len(events_ust) == 0:
            del context_fields['userspace']

        basename = os.path.basename(args.config_file)
        basename = basename.split('.')[0]

        basename = path.append_timestamp(basename)

        output_dir = os.path.normpath(os.path.expanduser(os.path.join(base_path, basename)))

        os.makedirs(output_dir, exist_ok=True)
        shutil.copyfile(args.config_file, os.path.join(output_dir, 'config.yaml'))

        launch_description.add_action(action=Trace(
            session_name=session_name,
            base_path=output_dir,
            append_timestamp=append_timestamp,
            events_kernel=events_kernel,
            events_ust=events_ust,
            context_fields=context_fields
        ))

        def on_start(event: launch.events.process.ProcessStarted,
                     context: launch.launch_context.LaunchContext) -> Optional[SomeActionsType]:
            if event.action.node_name in nodes:
                pid = event.pid

                return launch_ros.actions.Node(
                       name=f'topnode_{pid}',
                       namespace='',
                       package='topnode',
                       executable='resource_monitor',
                       output='screen',
                       parameters=[{
                           "publish_period_ms": 500,
                           "record_cpu_memory_usage": True,
                           "record_memory_state": True,
                           "record_io_stats": True,
                           "record_stat": True,
                           "record_file": f'{output_dir}{event.action.node_name}_{pid}.mcap',
                           "pid": pid
                        }])

        if 'topnode' in config and 'nodes' in config['topnode']:
                nodes = config['topnode']['nodes']
                launch_description.add_action(launch.actions.RegisterEventHandler(
                        launch.event_handlers.OnProcessStart(on_start=on_start)
                ))

        launch_service = launch.LaunchService()
        launch_service.include_launch_description(launch_description)
        return launch_service.run()
