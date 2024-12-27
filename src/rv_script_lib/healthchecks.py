from typing import Literal, Optional, Self
from urllib.parse import urlunparse

import requests

from rv_script_lib.logging import custom_logger_proxy

HEALTHCHECK_DEFAULT_PROTOCOL = "https"
HEALTHCHECK_DEFAULT_HOSTNAME = "hc-ping.com"


class HealthCheckPinger:
    def __init__(
        self: Self,
        uuid: str,
        healthcheck_protocol: Optional[
            Literal["http", "https"]
        ] = HEALTHCHECK_DEFAULT_PROTOCOL,
        healtheck_host: Optional[str] = "hc-ping.com",
    ) -> Self:
        self.log = custom_logger_proxy()
        self.uuid = uuid
        self.healthcheck_protocol = healthcheck_protocol
        self.healtheck_host = healtheck_host

    def __call_hc_api(
        self: Self,
        endpoint_path: str,
        endpoint_name: str,
        params: Optional[dict] = None,
        data: Optional[str] = None,
    ) -> bool:
        if not self.uuid:
            self.log.debug("Healthcheck uuid not set, skipping")
            return

        url = urlunparse(
            (
                self.healthcheck_protocol,
                self.healtheck_host,
                endpoint_path,
                "",
                "",
                "",
            )
        )

        self.log.debug("Calling Healthcheck", endpoint=endpoint_name, url=url)

        resp = requests.post(url, params=params, data=data)

        if "(not found)" in resp.text.lower():
            self.log.warning("Healthcheck not found", endpoint=endpoint_name, url=url)
            return False

        if "(rate limited)" in resp.text.lower():
            self.log.warning(
                "Healthcheck rate limited", endpoint=endpoint_name, url=url
            )
            return False

        try:
            resp.raise_for_status()
            return True
        except Exception as e:
            self.log.exception(e)

        return False

    @staticmethod
    def __get_optional_params(**hc_kwargs) -> dict:
        return {key: value for key, value in hc_kwargs.items() if bool(value)}

    def success(self: Self, rid: Optional[str] = ""):
        self.__call_hc_api(
            endpoint_path=f"/{self.uuid}",
            endpoint_name="success",
            params=self.__get_optional_params(rid=rid),
        )

    def start(self: Self, rid: Optional[str] = ""):
        self.__call_hc_api(
            endpoint_path=f"/{self.uuid}/start",
            endpoint_name="start",
            params=self.__get_optional_params(rid=rid),
        )

    def fail(self: Self, rid: Optional[str] = ""):
        self.__call_hc_api(
            endpoint_path=f"/{self.uuid}/fail",
            endpoint_name="fail",
            params=self.__get_optional_params(rid=rid),
        )

    def log(self: Self, log_event: str, rid: Optional[str] = ""):
        self.__call_hc_api(
            endpoint_path=f"/{self.uuid}/log",
            endpoint_name="log",
            params=self.__get_optional_params(rid=rid),
            data=log_event,
        )

    def exit_status(self: Self, exit_status: int, rid: Optional[str] = ""):
        if not isinstance(exit_status, int):
            self.log.error(
                "Aborting", reason="exit status is not integer", exit_status=exit_status
            )
            return
        if not 0 <= exit_status <= 255:
            self.log.error(
                "Aborting",
                reason="exit status needs to be in range 0-255",
                exit_status=exit_status,
            )
            return

        self.__call_hc_api(
            endpoint_path=f"/{self.uuid}/{exit_status}",
            endpoint_name="log",
            params=self.__get_optional_params(rid=rid),
        )
