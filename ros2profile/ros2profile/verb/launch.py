from ros2profile.verb import VerbExtension

from ros2profile.api.launch import expand_configuration

import launch

class LaunchVerb(VerbExtension):
    def add_arguments(self, parser, cli_name):  #noqa: D102
        parser.add_argument(
            'profile_config', help='Configuration to profile'
        )

    def main(self, *, args):
        launch_description = expand_configuration(args.profile_config)

        print(launch.LaunchIntrospector().format_launch_description(launch_description))
        launch_service = launch.LaunchService()
        launch_service.include_launch_description(launch_description)
        ret = launch_service.run()
