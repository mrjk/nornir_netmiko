# nornir_netmiko
Netmiko Plugins for [Nornir](https://github.com/nornir-automation/nornir)


## Installation

```bash
pip install nornir_netmiko
```

## Plugins

### Connections

- netmiko - Connect to network devices using netmiko

### Tasks

- netmiko_commit - Execute Netmiko commit method
- netmiko_file_transfer - Execute Netmiko file_transfer method
- netmiko_multiline - Execute Netmiko send_multiline method (or send_multiline_timing)
- netmiko_save_config - Execute Netmiko save_config method
- netmiko_send_command - Execute Netmiko send_command method (or send_command_timing)
- netmiko_send_config - Execute Netmiko send_config_set method (or send_config_from_file)


## Connection Options

### Platform

For better usability for napalm and netmiko users, the connection plugin maps the NAPALM base device types into netmiko device types:

```python
napalm_to_netmiko_map = {
    "ios": "cisco_ios",
    "nxos": "cisco_nxos",
    "nxos_ssh": "cisco_nxos",
    "eos": "arista_eos",
    "junos": "juniper_junos",
    "iosxr": "cisco_xr",
}
```

### Extras

The Connection Option `extras` are combined with the `host`, `username`, `password`, and `port` from the Host or Connection Object, and then passed to the ConnectHandler.

```yaml
router1:
  username: cisco
  platform: ios
  connection_options:
    netmiko:
      extras:
        secret: secret
        session_log: router1.txt
```

### Extra Netmiko platforms

Netmiko does not easily let you add new custom platforms, thus a custom injection mechanism is provided via the `nornir_netmiko` plugin. To add a new platform, you need to provide `netmiko_extra_platforms` dictionnary, in the `user_defined` configuration of `InitNornir`. The key represent the platform name, while the value is the class to use.

```python

# Create a new device_type derived from linux
from netmiko.linux.linux_ssh import LinuxSSH,

class CustomSSH(LinuxSSH):
    "Override LinuxSSH"

    def _build_ssh_client(self) -> SSHClient:
        """Allow passwordless authentication for HP devices being provisioned."""

        print("Hello World from CustomSSH")
        return super()._build_ssh_client()



# When instanciating Nornir, just provide a mapping
nr = InitNornir(
    user_defined= {
        "netmiko_extra_platforms": {
                "linux_embedded": CustomSSH,
            }
        }
    )
```
