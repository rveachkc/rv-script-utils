import argparse

from typing import Literal, Optional

from rv_script_lib.logging import (
    LOGLEVEL_FORMATTERS,
    DEFAULT_LOG_FORMAT,
    get_custom_logger,
)
from rv_script_lib.healthchecks import (
    HEALTHCHECK_DEFAULT_PROTOCOL,
    HEALTHCHECK_DEFAULT_HOSTNAME,
)


def get_custom_parser(
    verbosity_config: Optional[Literal["bool", "count"]] = "bool",
    allow_format_choice: Optional[bool] = True,
    argparse_kwargs: Optional[dict] = {},
    include_healthchecks: Optional[bool] = True,
) -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(**argparse_kwargs)

    log_arg_group = parser.add_argument_group("Logging Options")

    if verbosity_config == "count":

        log_arg_group.add_argument(
            "-v",
            "--verbose",
            action="count",
            dest="log_verbosity",
            default=0,
            help="Log Verbosity, default warn, -v info, -vv debug",
        )
    else:

        log_arg_group.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            dest="log_verbosity",
            default=False,
            help="Log Verbosity, default info, debug when passed",
        )

    if allow_format_choice:

        log_arg_group.add_argument(
            "--log-format",
            dest="log_format",
            choices=sorted(LOGLEVEL_FORMATTERS.keys()),
            default=DEFAULT_LOG_FORMAT,
            help=f"Log format, default={DEFAULT_LOG_FORMAT}",
        )

    if include_healthchecks:

        hc_group = parser.add_argument_group("Healthcheck Options")
        hc_group.add_argument(
            "--healthcheck-protocol",
            dest="healthcheck_protocol",
            type=str,
            default=HEALTHCHECK_DEFAULT_PROTOCOL,
            help=argparse.SUPPRESS,
        )

        hc_group.add_argument(
            "--healthcheck-host",
            dest="healthcheck_host",
            type=str,
            default=HEALTHCHECK_DEFAULT_HOSTNAME,
            help=f"Healthcheck Hostname: Default {HEALTHCHECK_DEFAULT_HOSTNAME}",
        )
        hc_group.add_argument(
            "--healthcheck-uuid",
            dest="healthcheck_uuid",
            type=str,
            default="",
            help="Healthcheck UUID",
        )

    return parser


def get_logger_from_args(
    args: argparse.Namespace,
    log_initialization: Optional[bool] = False,
    force_log_format: Optional[str] = "",
):

    if force_log_format in LOGLEVEL_FORMATTERS.keys():
        use_log_format = force_log_format
    elif "log_format" in args:
        use_log_format = args.log_format
    else:
        use_log_format = DEFAULT_LOG_FORMAT

    return get_custom_logger(
        log_format=use_log_format,
        loglevel_argument=args.log_verbosity,
        log_initialization=log_initialization,
    )
