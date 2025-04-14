from os import path

from netmiko.linux.linux_ssh import LinuxSSH, LinuxFileTransfer
from paramiko import SSHClient
from netmiko.ssh_auth import SSHClient_noauth


class LinuxEmbeddedSSH(LinuxSSH):
    "Override class"

    def _build_ssh_client(self) -> SSHClient:
        """Allow passwordless authentication for HP devices being provisioned."""

        # Create instance of SSHClient object. If no SSH keys and no password, then use noauth
        remote_conn_pre: SSHClient
        if not self.use_keys and not self.password:
            remote_conn_pre = SSHClient_noauth()
        else:
            remote_conn_pre = SSHClient()

        # Load host_keys for better SSH security
        if self.system_host_keys:
            remote_conn_pre.load_system_host_keys()
        if self.alt_host_keys and path.isfile(self.alt_key_file):
            remote_conn_pre.load_host_keys(self.alt_key_file)

        # Default is to automatically add untrusted hosts (make sure appropriate for your env)
        remote_conn_pre.set_missing_host_key_policy(self.key_policy)
        return remote_conn_pre

    def cleanup(self, command: str = "exit") -> None:
        """Gracefully exit the SSH session."""

        try:
            if self.username != "root" and self.check_config_mode():
                self.exit_config_mode()
        except Exception:
            pass
        # Always try to send final 'exit' (command)
        if self.session_log:
            self.session_log.fin = True
        self.write_channel(command + self.RETURN)


class LinuxEmbeddedFileTransfer(LinuxFileTransfer):
    """
    Linux SCP File Transfer driver.

    Mostly for testing purposes.
    """
