# import argparse

from typing import Self

# from rv_script_lib.arguments import get_logger_from_args
from rv_script_lib.arguments import get_custom_parser, get_logger_from_args
from rv_script_lib.healthchecks import HealthCheckPinger


# , args: argparse.Namespace
class ScriptBase:

    PARSER_VERBOSITY_CONFIG = "bool"
    PARSER_ALLOW_FORMAT_CHOICE = True
    PARSER_INCLUDE_HEALTHCHECKS = True
    PARSER_ARGPARSE_KWARGS = {}

    def __init__(self: Self) -> Self:

        self.parser = get_custom_parser(
            verbosity_config=self.PARSER_VERBOSITY_CONFIG,
            allow_format_choice=self.PARSER_ALLOW_FORMAT_CHOICE,
            argparse_kwargs=self.PARSER_ARGPARSE_KWARGS,
            include_healthchecks=self.PARSER_INCLUDE_HEALTHCHECKS,
        )

        self.extraArgs()

        self.args = self.parser.parse_args()

        self.log = get_logger_from_args(self.args)

        if self.args.healthcheck_uuid:
            self.healthcheck = HealthCheckPinger(
                uuid=self.args.healthcheck_uuid,
                healthcheck_protocol=self.args.healthcheck_protocol,
                healtheck_host=self.args.healthcheck_host,
            )

    def extraArgs(self: Self):

        # self.parser.add_argument(...)
        pass

    # def init(self: Self):

    def run(self: Self):

        raise NotImplementedError("The run method should be overriden")
