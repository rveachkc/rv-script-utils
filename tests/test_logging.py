import logging
from typing import Self
from unittest import TestCase

from rv_script_lib.logging import (
    get_loglevel_from_arg,
)


class TestGetLoglevelFromArg(TestCase):
    def testNoneInput(self: Self):
        self.assertEqual(get_loglevel_from_arg(None), logging.INFO)

    def testBoolInput(self: Self):
        self.assertEqual(get_loglevel_from_arg(False), logging.INFO)
        self.assertEqual(get_loglevel_from_arg(True), logging.DEBUG)

    def testLoggingInputs(self: Self):
        self.assertEqual(get_loglevel_from_arg(logging.DEBUG), logging.DEBUG)
        self.assertEqual(get_loglevel_from_arg(logging.INFO), logging.INFO)
        self.assertEqual(get_loglevel_from_arg(logging.WARN), logging.WARN)
        self.assertEqual(get_loglevel_from_arg(logging.ERROR), logging.ERROR)
        self.assertEqual(get_loglevel_from_arg(logging.CRITICAL), logging.CRITICAL)

    def testCountInputs(self: Self):
        self.assertEqual(get_loglevel_from_arg(2), logging.DEBUG)
        self.assertEqual(get_loglevel_from_arg(1), logging.INFO)
        self.assertEqual(get_loglevel_from_arg(0), logging.WARN)

    def testUnexpectedValues(self: Self):
        self.assertEqual(get_loglevel_from_arg(5), logging.DEBUG)
        self.assertEqual(get_loglevel_from_arg(150), logging.DEBUG)
        self.assertEqual(get_loglevel_from_arg(151), logging.DEBUG)
