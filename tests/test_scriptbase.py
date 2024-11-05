from unittest import TestCase, mock
from typing import Self

import structlog
from structlog.testing import capture_logs

from rv_script_lib import ScriptBase


class TestScriptBase(TestCase):

    def setUp(self: Self):
        structlog.reset_defaults()
        self.assertFalse(structlog.is_configured())

    @mock.patch("sys.argv", ["script_name"])
    def test_not_implemented(self: Self):
        """
        set arguments to be basic, as we want to limit our logging options
        """

        job = ScriptBase()

        with capture_logs() as cap_logs:

            with self.assertRaises(NotImplementedError):
                job.run()

        import pprint

        pprint.pprint(cap_logs)

        exception_logs = [x for x in cap_logs if x.get("exc_info")]

        self.assertEqual(len(exception_logs), 1)
