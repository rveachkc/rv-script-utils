import datetime
from itertools import count
from time import sleep
from typing import Self

from prometheus_client import CollectorRegistry, Counter, Gauge, write_to_textfile
from pytimeparse import parse as timeparse

from rv_script_lib.arguments import get_custom_parser, get_logger_from_args
from rv_script_lib.healthchecks import HealthCheckPinger


class ScriptBase:
    PARSER_VERBOSITY_CONFIG = "bool"
    FORCE_LOG_FORMAT = ""
    PARSER_INCLUDE_HEALTHCHECKS = True
    PARSER_ARGPARSE_KWARGS = {}
    PARSER_INCLUDE_REPEAT_OPTIONS = False
    LOG_INITIALIZATION = True
    PROM_METRIC_PREFIX = "scriptbase"

    def __init__(self: Self) -> Self:
        self.parser = get_custom_parser(
            verbosity_config=self.PARSER_VERBOSITY_CONFIG,
            allow_format_choice=not bool(self.FORCE_LOG_FORMAT),
            argparse_kwargs=self.PARSER_ARGPARSE_KWARGS,
            include_healthchecks=self.PARSER_INCLUDE_HEALTHCHECKS,
            include_repeat_group=self.PARSER_INCLUDE_REPEAT_OPTIONS,
        )

        self.extraArgs()

        self.args = self.parser.parse_args()

        self.log = get_logger_from_args(
            args=self.args,
            log_initialization=self.LOG_INITIALIZATION,
            force_log_format=self.FORCE_LOG_FORMAT,
        )

        self.prom_registry = CollectorRegistry()

        self.prom_success = Gauge(
            f"{self.PROM_METRIC_PREFIX}_success",
            "1 if successful, 0 if not",
            registry=self.prom_registry,
        )

        if self.args.repeat_interval:
            self.repeat_interval = datetime.timedelta(
                seconds=timeparse(self.args.repeat_interval)
            )
            self.log.info("interval set", interval=str(self.repeat_interval))
            self.prom_repeat_count = Counter(
                f"{self.PROM_METRIC_PREFIX}_repeat_count",
                "Number of times a script has been run",
                ["status"],
                registry=self.prom_registry,
            )

        self.extraMetrics()

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

    def extraMetrics(self: Self):
        # override this to add additional prometheus metrics
        # self.new_metric = Counter("name", "help", ["labels"], registry=self.prom_registry)
        pass

    def runJob(self: Self):
        # override this to define the job that should be done

        raise NotImplementedError("The run method should be overriden")

    def __run_job_runner(self: Self):
        """
        internal method to send the healthcheck, run the job, and log any exceptions.
        """
        self.healthcheck.start()

        if self.args.repeat_interval:
            self.prom_repeat_count.labels("total").inc()

        try:
            self.runJob()

        except Exception as e:
            self.log.exception(e)

            self.prom_success.set(0)
            if self.args.repeat_interval:
                self.prom_repeat_count.labels("fail").inc()

            self.healthcheck.fail()
            raise

        self.prom_success.set(1)
        if self.args.repeat_interval:
            self.prom_repeat_count.labels("success").inc()

        if self.args.prom_textfile:
            self.log.debug("Writing Prometheus textfile", path=self.args.prom_textfile)
            write_to_textfile(self.args.prom_textfile, self.prom_registry)

        self.healthcheck.success()

    def run(self: Self):
        """
        main method that should be called by the user's script.
        """

        if all(
            [
                bool(self.args.repeat_interval),
                self.args.repeat_max > 0,
            ]
        ):
            for i in range(1, (self.args.repeat_max + 1)):
                self.log.debug("repeat loop", i=i, max=self.args.repeat_max)
                self.__run_job_runner()
                sleep(self.repeat_interval.total_seconds())

        elif bool(self.args.repeat_interval):
            for i in count(start=1, step=1):
                self.log.debug("repeat loop", i=i, max=self.args.repeat_max)
                self.__run_job_runner()
                sleep(self.repeat_interval.total_seconds())

        else:
            self.__run_job_runner()
