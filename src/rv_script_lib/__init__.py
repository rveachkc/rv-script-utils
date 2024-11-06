from typing import Self

from rv_script_lib.arguments import get_custom_parser, get_logger_from_args
from rv_script_lib.healthchecks import HealthCheckPinger


class ScriptBase:

    PARSER_VERBOSITY_CONFIG = "bool"
    FORCE_LOG_FORMAT = ""
    PARSER_INCLUDE_HEALTHCHECKS = True
    PARSER_ARGPARSE_KWARGS = {}
    LOG_INITIALIZATION = True

    def __init__(self: Self) -> Self:

        self.parser = get_custom_parser(
            verbosity_config=self.PARSER_VERBOSITY_CONFIG,
            allow_format_choice=not bool(self.FORCE_LOG_FORMAT),
            argparse_kwargs=self.PARSER_ARGPARSE_KWARGS,
            include_healthchecks=self.PARSER_INCLUDE_HEALTHCHECKS,
        )

        self.extraArgs()

        self.args = self.parser.parse_args()

        self.log = get_logger_from_args(
            args=self.args,
            log_initialization=self.LOG_INITIALIZATION,
            force_log_format=self.FORCE_LOG_FORMAT,
        )

        try:
            self.healthcheck = HealthCheckPinger(
                uuid=self.args.healthcheck_uuid,
                healthcheck_protocol=self.args.healthcheck_protocol,
                healtheck_host=self.args.healthcheck_host,
            )
        except AttributeError:
            self.healthcheck = HealthCheckPinger(
                uuid="",
            )

    def extraArgs(self: Self):
        # override this to add additional arguments

        # self.parser.add_argument(...)
        pass

    def runJob(self: Self):
        # override this to define the job that should be done

        raise NotImplementedError("The run method should be overriden")

    def run(self: Self):

        self.healthcheck.start()

        try:
            self.runJob()

        except Exception as e:
            self.log.exception(e)
            self.healthcheck.fail()
            raise

        self.healthcheck.success()
