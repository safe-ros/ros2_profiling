from ros2profile.verb import VerbExtension

from ros2profile.api.process import process

import tracetools_analysis.process

class ProcessVerb(VerbExtension):
    def add_arguments(self, parser, cli_name):  #noqa: D102
        parser.add_argument(
            'input_path', help='Directory where profile output is stored'
        )

    def main(self, *, args):
        # Process the trace
        tracetools_analysis.process.process(
                args.input_path + 'ros2profile-tracing-session', False, True, False)

        # Process topnode results
        process(args.input_path)
