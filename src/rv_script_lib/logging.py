import logging
import os
import sys

from typing import Optional, Literal, Union

import structlog

DEFAULT_LOG_FORMAT = "dev"

LOGLEVEL_FORMATTERS = {
    "logfmt": structlog.processors.LogfmtRenderer(),
    "json": structlog.processors.JSONRenderer(),
    "dev": structlog.dev.ConsoleRenderer(),
}

TIMESTAMPER_KWARGS = {
    "dev": {
        "utc": False,
        "fmt": "iso",
    }
}


def get_loglevel_formatter_by_name(format_name: str):

    return LOGLEVEL_FORMATTERS.get(
        format_name, LOGLEVEL_FORMATTERS.get(DEFAULT_LOG_FORMAT)
    )


def get_loglevel_from_arg(loglevel_argument: Union[int, bool, None]) -> int:

    if loglevel_argument is None:
        return logging.INFO

    if isinstance(loglevel_argument, bool):
        return logging.DEBUG if loglevel_argument else logging.INFO

    if not isinstance(loglevel_argument, int):
        raise TypeError("This loglevelargument is expected to be None, bool, or int")

    if all(
        [
            50 >= loglevel_argument >= 10,
            loglevel_argument % 10 == 0,
        ]
    ):
        return loglevel_argument

    return {
        0: logging.WARN,
        1: logging.INFO,
    }.get(loglevel_argument, logging.DEBUG)


def get_custom_logger(
    log_format: Optional[Literal["logfmt", "json", "dev"]] = DEFAULT_LOG_FORMAT,
    force_configure: Optional[bool] = False,
    loglevel_argument: Union[int, bool] = logging.INFO,
    log_initialization: Optional[bool] = False,
) -> structlog.typing.WrappedLogger:

    log_level = get_loglevel_from_arg(loglevel_argument)

    if any(
        [
            not structlog.is_configured(),
            force_configure,
        ]
    ):

        configure_kwargs = TIMESTAMPER_KWARGS.get(
            log_format, LOGLEVEL_FORMATTERS[DEFAULT_LOG_FORMAT]
        )

        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.TimeStamper(**configure_kwargs),
                get_loglevel_formatter_by_name(log_format),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(log_level),
        )

    logger = structlog.get_logger()

    if log_initialization:
        logger.info(
            "initializing",
            executable=os.path.basename(sys.argv[0]),
            log_format=log_format,
            loglevel=logging.getLevelName(log_level),
        )

    return logger


def custom_logger_proxy() -> structlog.typing.WrappedLogger:

    return structlog.get_logger()
