from ros2profile.verb import VerbExtension

from ros2profile.api.run_test import run_test

class RunTestVerb(VerbExtension):
    def add_arguments(self, parser, cli_name):  #noqa: D102
        parser.add_argument(
            'input_path', help='Directory where profile output is stored'
        )

        parser.add_argument(
            'test_file', help='pytest file to run'
        )

    def main(self, *, args):
        return run_test(args.input_path, args.test_file)
