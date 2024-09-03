"""Library to control a sky box using python."""

# pylint: disable=too-few-public-methods
import socket
import time
import asyncio


class SkyBoxConnectionError(Exception):
    """Sky Box Connection Error."""


class ConnectionTimeoutError(SkyBoxConnectionError):
    """Connection Timeout Error."""


class NotASkyBoxError(SkyBoxConnectionError):
    """Device probably is not a Sky box error."""


class RemoteControl:
    """RemoteControl class of sky_remote."""

    def __init__(self, host, port=49160) -> None:
        """Set up the connection variables and keymap."""
        self.host = host
        self.port = port
        self.key_map = {
            "power": 0,
            "select": 1,
            "backup": 2,
            "dismiss": 2,
            "channelup": 6,
            "channeldown": 7,
            "interactive": 8,
            "sidebar": 8,
            "help": 9,
            "services": 10,
            "search": 10,
            "tvguide": 11,
            "home": 11,
            "i": 14,
            "text": 15,
            "up": 16,
            "down": 17,
            "left": 18,
            "right": 19,
            "red": 32,
            "green": 33,
            "yellow": 34,
            "blue": 35,
            "0": 48,
            "1": 49,
            "2": 50,
            "3": 51,
            "4": 52,
            "5": 53,
            "6": 54,
            "7": 55,
            "8": 56,
            "9": 57,
            "play": 64,
            "pause": 65,
            "stop": 66,
            "record": 67,
            "fastforward": 69,
            "rewind": 71,
            "boxoffice": 240,
            "sky": 241,
        }

    async def check_connectable(self, timeout=3) -> bool:
        """Return True if device is probably a Sky box."""
        connection_future = asyncio.open_connection(self.host, self.port)
        try:
            reader, writer = await asyncio.wait_for(connection_future, timeout)
        except asyncio.TimeoutError as e:
            raise ConnectionTimeoutError from e
        try:
            data = await asyncio.wait_for(reader.read(3), timeout)
        except asyncio.TimeoutError as e:
            raise NotASkyBoxError from e
        if data != bytes("SKY", "ascii"):
            raise NotASkyBoxError

        writer.close()
        await writer.wait_closed()
        return True

    def send_keys(self, key_list, time_spacing=0.01):
        """Send a single key or list of keys to the sky box."""
        if isinstance(key_list, list):
            for item in key_list:
                if item not in self.key_map:
                    raise ValueError(f"Invalid key: {item}")
                self._send_key(item)
                time.sleep(time_spacing)
        elif key_list not in self.key_map:
            raise ValueError(f"Invalid key: {key_list}")
        else:
            self._send_key(key_list)

    def _send_key(self, key):
        """Open connection to sky box and send a key command."""
        if key not in self.key_map:
            raise ValueError(f"Invalid key: {key}")

        code = self.key_map[key]
        command_bytes = [4, 1, 0, 0, 0, 0, 224 + (code // 16), code % 16]
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            client.connect((self.host, self.port))
            length = 12

            while True:
                data = client.recv(1024)  # Receive data from the server

                if not data:
                    break  # No more data, exit loop

                if len(data) < 24:
                    client.send(data[:length])  # Send a portion of received data
                    length = 1  # Reduce `length` for subsequent sends
                else:
                    client.send(bytes(command_bytes))  # Send the command bytes
                    command_bytes[1] = 0
                    client.send(bytes(command_bytes))  # Send modified command bytes again
                    return None
        finally:
            client.close()  # Ensure the socket connection is closed
