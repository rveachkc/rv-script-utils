import argparse
from collections import Counter
from typing import Self
from unittest import TestCase

import structlog
from structlog.testing import capture_logs

from rv_script_lib.arguments import get_custom_parser, get_logger_from_args


class TestArguments(TestCase):
    def setUp(self: Self):
        structlog.reset_defaults()
        self.assertFalse(structlog.is_configured())

    @staticmethod
    def do_log_entries(logger) -> tuple[list, dict]:
        """
        We want to run the same battery of log entries against each of the configs
        This will make that repeatable and return a dictionary containing counts from each log level
        """

        with capture_logs() as cap_logs:
            logger.critical("oh no!")
            logger.error("error message")
            logger.warning("This is a warning", thing1="thing2")
            logger.info("Test Info Logging", key="value")
            logger.debug("This is debug")

        log_levels = map(
            lambda x: x.get("log_level"),
            cap_logs,
        )

        counts = Counter(log_levels).most_common()

        counts = {x[0]: x[1] for x in counts}

        return cap_logs, counts

    def test_defaults(self: Self):
        # get parser with default values
        parser = get_custom_parser()

        self.assertIsInstance(parser, argparse.ArgumentParser)

        # parse with no arguments
        args = parser.parse_args([])

        self.assertIsInstance(args, argparse.Namespace)

        logger = get_logger_from_args(args)

        self.assertTrue(structlog.is_configured())

        cap_logs, log_counts = self.do_log_entries(logger)

        # the default args should filter out debug logging
        self.assertEqual(len(cap_logs), 4)

        self.assertEqual(log_counts.get("debug", 0), 0)
        self.assertEqual(log_counts.get("info", 0), 1)
        self.assertEqual(log_counts.get("warning", 0), 1)
        self.assertEqual(log_counts.get("error", 0), 1)
        self.assertEqual(log_counts.get("critical", 0), 1)

    def test_defaults_verbose(self: Self):
        # get parser with default values
        parser = get_custom_parser()

        # parse with no arguments
        args = parser.parse_args(["-v"])

        logger = get_logger_from_args(args)

        self.assertTrue(structlog.is_configured())

        cap_logs, log_counts = self.do_log_entries(logger)

        # the default args should filter out debug logging
        self.assertEqual(len(cap_logs), 5)

        self.assertEqual(log_counts.get("debug", 0), 1)
        self.assertEqual(log_counts.get("info", 0), 1)
        self.assertEqual(log_counts.get("warning", 0), 1)
        self.assertEqual(log_counts.get("error", 0), 1)
        self.assertEqual(log_counts.get("critical", 0), 1)

    def test_bool_defaults(self: Self):
        # get parser with default values
        parser = get_custom_parser(verbosity_config="count")

        # parse with no arguments
        args = parser.parse_args([])

        logger = get_logger_from_args(args)

        self.assertTrue(structlog.is_configured())

        cap_logs, log_counts = self.do_log_entries(logger)

        # the default args should filter out debug logging
        self.assertEqual(len(cap_logs), 3)

        self.assertEqual(log_counts.get("debug", 0), 0)
        self.assertEqual(log_counts.get("info", 0), 0)
        self.assertEqual(log_counts.get("warning", 0), 1)
        self.assertEqual(log_counts.get("error", 0), 1)
        self.assertEqual(log_counts.get("critical", 0), 1)

    def test_bool_v(self: Self):
        # get parser with default values
        parser = get_custom_parser(verbosity_config="count")

        # parse with no arguments
        args = parser.parse_args(["-v"])

        logger = get_logger_from_args(args)

        self.assertTrue(structlog.is_configured())

        cap_logs, log_counts = self.do_log_entries(logger)

        # the default args should filter out debug logging
        self.assertEqual(len(cap_logs), 4)

        self.assertEqual(log_counts.get("debug", 0), 0)
        self.assertEqual(log_counts.get("info", 0), 1)
        self.assertEqual(log_counts.get("warning", 0), 1)
        self.assertEqual(log_counts.get("error", 0), 1)
        self.assertEqual(log_counts.get("critical", 0), 1)

    def test_bool_vv(self: Self):
        # get parser with default values
        parser = get_custom_parser(verbosity_config="count")

        # parse with no arguments
        args = parser.parse_args(["-vv"])

        logger = get_logger_from_args(args)

        self.assertTrue(structlog.is_configured())

        cap_logs, log_counts = self.do_log_entries(logger)

        # the default args should filter out debug logging
        self.assertEqual(len(cap_logs), 5)

        self.assertEqual(log_counts.get("debug", 0), 1)
        self.assertEqual(log_counts.get("info", 0), 1)
        self.assertEqual(log_counts.get("warning", 0), 1)
        self.assertEqual(log_counts.get("error", 0), 1)
        self.assertEqual(log_counts.get("critical", 0), 1)
