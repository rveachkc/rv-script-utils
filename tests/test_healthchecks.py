from typing import Self
from unittest import TestCase

import requests_mock

from rv_script_lib.healthchecks import HealthCheckPinger


class TestHealthCheckPinger(TestCase):
    # this is what is in the http api documentation
    # https://healthchecks.io/docs/http_api/
    TEST_UUID = "5bf66975-d4c7-4bf5-bcc8-b8d8a82ea278"

    def setUp(self: Self):
        self.healthcheck = HealthCheckPinger(uuid=self.TEST_UUID)

    @requests_mock.Mocker()
    def test_call_api_success(self: Self, rmock: requests_mock.mocker.Mocker):
        rmock.post(f"https://hc-ping.com/{self.TEST_UUID}", text="OK")

        result = self.healthcheck._HealthCheckPinger__call_hc_api(
            endpoint_path=f"/{self.TEST_UUID}",
            endpoint_name="success",
        )
        self.assertTrue(result)
        self.assertTrue(rmock.called)
        self.assertEqual(rmock.call_count, 1)

    @requests_mock.Mocker()
    def test_call_api_not_found(self: Self, rmock: requests_mock.mocker.Mocker):
        rmock.post(f"https://hc-ping.com/{self.TEST_UUID}", text="OK (not found)")

        result = self.healthcheck._HealthCheckPinger__call_hc_api(
            endpoint_path=f"/{self.TEST_UUID}",
            endpoint_name="success",
        )
        self.assertFalse(result)
        self.assertTrue(rmock.called)
        self.assertEqual(rmock.call_count, 1)

    @requests_mock.Mocker()
    def test_call_api_rate_limit(self: Self, rmock: requests_mock.mocker.Mocker):
        rmock.post(f"https://hc-ping.com/{self.TEST_UUID}", text="(rate limited)")

        result = self.healthcheck._HealthCheckPinger__call_hc_api(
            endpoint_path=f"/{self.TEST_UUID}",
            endpoint_name="success",
        )

        self.assertFalse(result)
        self.assertTrue(rmock.called)
        self.assertEqual(rmock.call_count, 1)

    @requests_mock.Mocker()
    def test_call_success(self: Self, rmock: requests_mock.mocker.Mocker):
        rmock.post(f"https://hc-ping.com/{self.TEST_UUID}", text="(rate limited)")

        self.healthcheck.success()
        self.assertTrue(rmock.called)
        self.assertEqual(rmock.call_count, 1)

    @requests_mock.Mocker()
    def test_call_start(self: Self, rmock: requests_mock.mocker.Mocker):
        rmock.post(f"https://hc-ping.com/{self.TEST_UUID}/start", text="(rate limited)")

        self.healthcheck.start()
        self.assertTrue(rmock.called)
        self.assertEqual(rmock.call_count, 1)

    @requests_mock.Mocker()
    def test_call_fail(self: Self, rmock: requests_mock.mocker.Mocker):
        rmock.post(f"https://hc-ping.com/{self.TEST_UUID}/fail", text="(rate limited)")

        self.healthcheck.fail()
        self.assertTrue(rmock.called)
        self.assertEqual(rmock.call_count, 1)


class TestHealthCheckEmpty(TestCase):
    TEST_UUID = ""

    def setUp(self: Self):
        self.healthcheck = HealthCheckPinger(uuid=self.TEST_UUID)

    @requests_mock.Mocker()
    def test_call_success(self: Self, rmock: requests_mock.mocker.Mocker):
        rmock.post(f"https://hc-ping.com/{self.TEST_UUID}", text="(rate limited)")

        self.healthcheck.success()
        self.assertFalse(rmock.called)

    @requests_mock.Mocker()
    def test_call_start(self: Self, rmock: requests_mock.mocker.Mocker):
        rmock.post(f"https://hc-ping.com/{self.TEST_UUID}/start", text="(rate limited)")

        self.healthcheck.start()
        self.assertFalse(rmock.called)

    @requests_mock.Mocker()
    def test_call_fail(self: Self, rmock: requests_mock.mocker.Mocker):
        rmock.post(f"https://hc-ping.com/{self.TEST_UUID}/fail", text="(rate limited)")

        self.healthcheck.fail()
        self.assertFalse(rmock.called)


class TestHealthCheckNone(TestCase):
    TEST_UUID = None

    def setUp(self: Self):
        self.healthcheck = HealthCheckPinger(uuid=self.TEST_UUID)

    @requests_mock.Mocker()
    def test_call_success(self: Self, rmock: requests_mock.mocker.Mocker):
        rmock.post(f"https://hc-ping.com/{self.TEST_UUID}", text="(rate limited)")

        self.healthcheck.success()
        self.assertFalse(rmock.called)

    @requests_mock.Mocker()
    def test_call_start(self: Self, rmock: requests_mock.mocker.Mocker):
        rmock.post(f"https://hc-ping.com/{self.TEST_UUID}/start", text="(rate limited)")

        self.healthcheck.start()
        self.assertFalse(rmock.called)

    @requests_mock.Mocker()
    def test_call_fail(self: Self, rmock: requests_mock.mocker.Mocker):
        rmock.post(f"https://hc-ping.com/{self.TEST_UUID}/fail", text="(rate limited)")

        self.healthcheck.fail()
        self.assertFalse(rmock.called)
