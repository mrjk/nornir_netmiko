from typing import Any, Dict, Optional

from netmiko import ConnectHandler
from netmiko.ssh_dispatcher import platforms

from nornir.core.configuration import Config


CONNECTION_NAME = "netmiko"

napalm_to_netmiko_map = {
    "ios": "cisco_ios",
    "nxos": "cisco_nxos",
    "nxos_ssh": "cisco_nxos",
    "eos": "arista_eos",
    "junos": "juniper_junos",
    "iosxr": "cisco_xr",
}


class Netmiko:
    """
    This plugin connects to the device using the Netmiko driver and sets the
    relevant connection.
    Inventory:
        extras: maps to argument passed to ``ConnectHandler``.
    """

    def open(
        self,
        hostname: Optional[str],
        username: Optional[str],
        password: Optional[str],
        port: Optional[int],
        platform: Optional[str],
        extras: Optional[Dict[str, Any]] = None,
        configuration: Optional[Config] = None,
    ) -> None:
        parameters = {
            "host": hostname,
            "username": username,
            "password": password,
            "port": port,
        }

        try:
            parameters[
                "ssh_config_file"
            ] = configuration.ssh.config_file  # type: ignore
        except AttributeError:
            pass

        if platform is not None:
            # Look platform up in corresponding map, if no entry return the host.nos unmodified
            platform = napalm_to_netmiko_map.get(platform, platform)
            parameters["device_type"] = platform

        # Allow nornir_netmiko to load extra platforms/device_types
        # See https://github.com/ktbyers/netmiko/issues/3252
        # There is no easy way to inject a new netmiko device_type, so we
        # completely skip the original ConnectHandler function. This makes
        # the extra platform only available via nornir_netmiko. Since this
        # is a tightly coupled integration, it should not be an issue.

        device_type = parameters["device_type"]
        connect_handler_cls = ConnectHandler
        connect_handlers_map = configuration.user_defined.get("netmiko_extra_platforms", {})
        assert isinstance(connect_handlers_map, dict), f"netmiko_extra_platforms must be a dict, got {type(connect_handlers_map)}"
        if device_type in connect_handlers_map:
            # If user provided a custom device_type, then directly use it and bypass
            # original ConnectHandler function.
            connect_handler_cls = connect_handlers_map[device_type]
        else:
            # Ensure device exists in netmiko package. We want
            # to let the user being notified of the actual platform list.
            if device_type not in platforms:
                extra_platforms = list(connect_handlers_map.keys())
                platform_names = '\n'.join(sorted(platforms + extra_platforms))
                raise ValueError(f"Unsupported device_type: {device_type}, currently supported platforms are:\n{platform_names}")

        extras = extras or {}
        parameters.update(extras)
        connection = connect_handler_cls(**parameters)
        self.connection = connection

    def close(self) -> None:
        self.connection.disconnect()
