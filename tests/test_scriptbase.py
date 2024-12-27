import datetime
import os
import pprint
from collections import Counter
from tempfile import TemporaryDirectory
from typing import Self
from unittest import TestCase, mock

import structlog
from structlog.testing import capture_logs

from rv_script_lib import ScriptBase


class TestScriptBase(TestCase):
    def setUp(self: Self):
        structlog.reset_defaults()
        self.assertFalse(structlog.is_configured())

    @staticmethod
    def count_loglevels(cap_logs: list) -> dict:
        log_levels = map(
            lambda x: x.get("log_level"),
            cap_logs,
        )

        level_counts = Counter(log_levels).most_common()

        return {x[0]: x[1] for x in level_counts}

    @mock.patch("sys.argv", ["script_name"])
    def test_not_implemented(self: Self):
        """
        set arguments to be basic, as we want to limit our logging options
        """

        job = ScriptBase()

        with capture_logs() as cap_logs:
            with self.assertRaises(NotImplementedError):
                job.run()

        pprint.pprint(cap_logs)

        exception_logs = [x for x in cap_logs if x.get("exc_info")]

        self.assertEqual(len(exception_logs), 1)

    @mock.patch("sys.argv", ["script_name", "-vv"])
    def test_basic_use(self: Self):
        class MyScript(ScriptBase):
            def runJob(self: Self):
                self.log.warning("hello")

        with capture_logs() as cap_logs:
            job = MyScript()
            job.run()

        pprint.pprint(cap_logs)

        level_counts = self.count_loglevels(cap_logs)
        pprint.pprint(level_counts)

        self.assertGreater(len(cap_logs), 1)

        # one for the init
        self.assertEqual(level_counts.get("info"), 1)

        # one for what we just defined
        self.assertEqual(level_counts.get("warning"), 1)

        self.assertIsInstance(job.args.log_verbosity, bool)

        # check to make sure the arg namespace has everything we need.
        for argname in (
            "log_verbosity",
            "log_format",
            "healthcheck_host",
            "healthcheck_uuid",
            "healthcheck_protocol",
        ):
            self.assertIn(argname, job.args)

    @mock.patch("sys.argv", ["script_name", "-vv", "--extra-arg", "penguin"])
    def test_extra_args(self: Self):
        class MyScript(ScriptBase):
            def extraArgs(self: Self):
                self.parser.add_argument(
                    "-x", "--extra-arg", type=str, dest="extra_arg"
                )

            def runJob(self: Self):
                self.found_extra_arg = self.args.extra_arg

        my_job = MyScript()
        self.assertIn("extra_arg", my_job.args)
        self.assertEqual(my_job.args.extra_arg, "penguin")
        self.assertTrue(my_job.args.log_verbosity)
        my_job.run()

        self.assertEqual(my_job.found_extra_arg, "penguin")

    @mock.patch("sys.argv", ["script_name", "-v", "--log-format", "logfmt"])
    def test_logfmt(self: Self):
        class MyScript(ScriptBase):
            def runJob(self: Self):
                pass

        my_job = MyScript()
        self.assertEqual(my_job.args.log_format, "logfmt")
        my_job.run()

    @mock.patch("sys.argv", ["script_name", "-vv", "--log-format", "json"])
    def test_json(self: Self):
        class MyScript(ScriptBase):
            def runJob(self: Self):
                pass

        my_job = MyScript()
        self.assertEqual(my_job.args.log_format, "json")
        my_job.run()

    @mock.patch("sys.argv", ["script_name", "-vv", "--log-format", "dev"])
    def test_dev(self: Self):
        class MyScript(ScriptBase):
            def runJob(self: Self):
                pass

        my_job = MyScript()
        self.assertEqual(my_job.args.log_format, "dev")
        my_job.run()

    @mock.patch("sys.argv", ["script_name", "-vv"])
    def test_force_format(self: Self):
        class MyScript(ScriptBase):
            FORCE_LOG_FORMAT = "json"

            def runJob(self: Self):
                pass

        my_job = MyScript()

        for argname in (
            "log_verbosity",
            "healthcheck_host",
            "healthcheck_uuid",
            "healthcheck_protocol",
        ):
            self.assertIn(argname, my_job.args)

        for argname in ("log_format",):
            self.assertNotIn(argname, my_job.args)

    @mock.patch("sys.argv", ["script_name", "-vv"])
    def test_disable_healthchecks(self: Self):
        class MyScript(ScriptBase):
            PARSER_INCLUDE_HEALTHCHECKS = False

            def runJob(self: Self):
                pass

        my_job = MyScript()

        for argname in (
            "log_format",
            "log_verbosity",
        ):
            self.assertIn(argname, my_job.args)

        for argname in (
            "healthcheck_host",
            "healthcheck_uuid",
            "healthcheck_protocol",
        ):
            self.assertNotIn(argname, my_job.args)

    @mock.patch("sys.argv", ["script_name"])
    def test_count_loglevel(self: Self):
        class MyScript(ScriptBase):
            PARSER_VERBOSITY_CONFIG = "count"

            def runJob(self: Self):
                pass

        my_job = MyScript()

        self.assertIsInstance(my_job.args.log_verbosity, int)
        self.assertEqual(my_job.args.log_verbosity, 0)

    @mock.patch("sys.argv", ["script_name", "-v"])
    def test_count_loglevel_v(self: Self):
        class MyScript(ScriptBase):
            PARSER_VERBOSITY_CONFIG = "count"

            def runJob(self: Self):
                pass

        my_job = MyScript()

        self.assertIsInstance(my_job.args.log_verbosity, int)
        self.assertEqual(my_job.args.log_verbosity, 1)

    @mock.patch("sys.argv", ["script_name", "-vv"])
    def test_count_loglevel_vv(self: Self):
        class MyScript(ScriptBase):
            PARSER_VERBOSITY_CONFIG = "count"

            def runJob(self: Self):
                pass

        my_job = MyScript()

        self.assertIsInstance(my_job.args.log_verbosity, int)
        self.assertEqual(my_job.args.log_verbosity, 2)

    @mock.patch("sys.argv", ["script_name"])
    def test_repeat_none(self: Self):
        class MyScript(ScriptBase):
            RUN_COUNT = 0

            def runJob(self: Self):
                self.RUN_COUNT += 1

        my_job = MyScript()
        my_job.run()

        self.assertEqual(my_job.RUN_COUNT, 1)

    @mock.patch(
        "sys.argv", ["script_name", "--repeat-interval", "0s", "--repeat-max", "5"]
    )
    def test_repeat_five(self: Self):
        class MyScript(ScriptBase):
            RUN_COUNT = 0

            def runJob(self: Self):
                self.RUN_COUNT += 1

        my_job = MyScript()
        my_job.run()

        self.assertEqual(my_job.RUN_COUNT, 5)

        self.assertIsInstance(my_job.repeat_interval, datetime.timedelta)

    @mock.patch("sys.argv", ["script_name", "--repeat-interval", "1h"])
    def test_repeat_parser(self: Self):
        class MyScript(ScriptBase):
            def runJob(self: Self):
                pass

        my_job = MyScript()

        self.assertIsInstance(my_job.repeat_interval, datetime.timedelta)
        self.assertEqual(my_job.repeat_interval.total_seconds(), 3600)


class TestScriptBaseTextfiles(TestCase):
    def setUp(self: Self):
        structlog.reset_defaults()
        self.assertFalse(structlog.is_configured())

        self.temp_dir = TemporaryDirectory()
        self.prom_textfile = os.path.join(self.temp_dir.name, "test.prom")

        self.assertFalse(os.path.isfile(self.prom_textfile))

    @mock.patch("sys.argv", ["script_name"])
    def test_no_arg(self: Self):
        class MyScript(ScriptBase):
            def runJob(self: Self):
                pass

        my_job = MyScript()
        my_job.run()

        self.assertFalse(os.path.isfile(self.prom_textfile))

    def test_write_textfile(self: Self):
        class MyScript(ScriptBase):
            def runJob(self: Self):
                pass

        # the decorator can't reference the class attribute
        with mock.patch(
            "sys.argv", ["script_name", "--prom-textfile", self.prom_textfile]
        ):
            my_job = MyScript()
            my_job.run()

        self.assertTrue(os.path.isfile(self.prom_textfile))
