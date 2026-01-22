import base64
import socket
from os import PathLike
from pathlib import Path
from typing import Any

from pysieved.main import Server


class MockConfig:
    def __init__(self, config: dict[str, dict[str, str | Any]]) -> None:
        self.config = config

    def get(self, section: str, key: str, default: Any | None = None) -> str | Any:
        try:
            return self.config[section][key]
        except KeyError:
            return default

    def getint(self, section: str, key: str, default: bool | None = None):
        return self.get(section, key, default)

    def getboolean(self, section: str, key: str, default: bool | None = None):
        return self.get(section, key, default)


class MockFilesystem:
    def __init__(self, base: str | PathLike, username: str) -> None:
        self.base = Path(base)

        if not self.base.exists():
            raise FileNotFoundError(f"Base folder '{base}' does not exist")

        self.filters = self.base.joinpath("mail", username[0], username, ".pysieved")
        self.filters.mkdir(exist_ok=True)

    def has_filter(self, name: str) -> bool:
        """Check if the filter exists in the mock filesystem."""

        return self.filters.joinpath(name).exists()

    def get_filter(self, name: str) -> bytes | None:
        """Get the content of a filter."""

        filter_path = self.filters.joinpath(name)

        if not filter_path.exists():
            return None

        with open(filter_path, "rb") as file:
            content = file.read()

        return content

    def remove_filter(self, name: str) -> bool:
        """Remove a filter from the filesystem."""

        filter_path = self.filters.joinpath(name)

        if not filter_path.exists():
            return False

        filter_path.unlink()

        return True

    def create_filter(self, name: str, content: bytes) -> bool:
        """Create a filter in the user's filesystem."""

        filter_path = self.filters.joinpath(name)

        if filter_path.exists():
            return False

        with open(filter_path, "wb") as file:
            file.write(content)

        return True


class MockClient:
    def __init__(self, server: Server) -> None:
        self.server = server
        self._is_authenticated = False

        self.BUF_SIZE = 4096

        address, port, *_ = self.server.socket.getsockname()

        self._default_timeout = 0.1

        try:
            # Try connecting with IPv6 first
            self.conn = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            self.conn.settimeout(self._default_timeout)
            self.conn.connect((address, port))
        except Exception:
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn.settimeout(self._default_timeout)
            self.conn.connect((address, port))

    def close(self) -> None:
        """Terminate client."""

        try:
            self.conn.shutdown(socket.SHUT_RDWR)
            self.conn.close()
        except Exception:
            pass

    def get_full_response(self) -> bytes:
        """Read all the received lines until the server stops responding until the timeout."""

        full_response = b""

        while True:
            try:
                part = self.conn.recv(self.BUF_SIZE)
            except Exception:
                break

            if not part:
                break

            full_response += part

        return full_response

    def _send(self, command: bytes) -> bytes:
        self.conn.send(command)
        return self.get_full_response()

    def authenticate(self, username: str, password: str) -> bytes | None:
        """Send an AUTHENTICATE command."""

        if self._is_authenticated:
            return

        credentials = f"\x00{username}\x00{password}"
        auth = base64.b64encode(credentials.encode()).decode()

        command = f'AUTHENTICATE "PLAIN" "{auth}"\r\n'
        self.conn.send(command.encode())

        response = self.get_full_response()
        self._is_authenticated = True

        return response

    def listscripts(self) -> bytes:
        """Send a LISTSCRIPTS command."""

        command = b"LISTSCRIPTS\r\n"
        return self._send(command)

    def capability(self) -> bytes:
        """Send a CAPABILITY command."""

        command = b"CAPABILITY\r\n"
        return self._send(command)

    def havespace(self, name: str, space: int | str) -> bytes:
        """Send a HAVESPACE command."""

        command = f'HAVESPACE "{name}" "{space}"\r\n'
        return self._send(command.encode())

    def putscript(
        self,
        name: str,
        content: bytes,
        size: int | None = None,
    ) -> bytes:
        """Send a PUTSCRIPT command."""

        self.conn.settimeout(2)

        if size is None:
            size = len(content)

        if not content.endswith(b"\r\n"):
            content += b"\r\n"

        byte_size = "{%d+}" % size
        command = f'PUTSCRIPT "{name}" {byte_size}\r\n'
        self.conn.sendall(command.encode())
        self.conn.sendall(content)

        response = self.get_full_response()

        self.conn.settimeout(self._default_timeout)

        return response

    def setactive(self, name: str | None = None) -> bytes:
        """Send a SETACTIVE command."""

        command = f'SETACTIVE "{name}"\r\n'
        if name is None:
            command = 'SETACTIVE ""\r\n'

        return self._send(command.encode())

    def getscript(self, name: str) -> bytes:
        """Send a GETSCRIPT command."""

        command = f'GETSCRIPT "{name}"\r\n'
        return self._send(command.encode())

    def deletescript(self, name: str) -> bytes:
        """Send a DELETESCRIPT command."""

        command = f'DELETESCRIPT "{name}"\r\n'
        return self._send(command.encode())

    def logout(self) -> bytes | None:
        """Send a LOGOUT command."""

        if not self._is_authenticated:
            return

        command = b"LOGOUT\r\n"
        return self._send(command)
