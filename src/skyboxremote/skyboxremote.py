"""Library to control a sky box using python."""

import socket
import time
import asyncio
import http.client
import logging

logger = logging.getLogger(__name__)


BOX_MODEL_DEFINITIONS = {
    # Note, leaving some SkyQ keys (dismiss, sidebar, home, search) within SkyHD
    # to ensure backwards compatibility with previous code. Previously, there
    # was no differentiation between different models.
    "skyhd": {
        "key_map": {
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
        },
        "power_state_upnp_uri": "/photo-viewing/start?uri=http://example.com/null.jpg",
    },
    "skyq": {
        "key_map": {
            "power": 0,
            "select": 1,
            "dismiss": 2,
            "channelup": 6,
            "channeldown": 7,
            "sidebar": 8,
            "help": 9,
            "search": 10,
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
        },
        "power_state_upnp_uri": "/photo-viewing/start?uri=http://example.com/null.jpg",
    },
}


class SkyBoxConnectionError(Exception):
    """Sky Box Connection Error."""


class ConnectionTimeoutError(SkyBoxConnectionError):
    """Connection Timeout Error."""


class NotASkyBoxError(SkyBoxConnectionError):
    """Device probably is not a Sky box error."""


class RemoteControl:
    """
    A library to control Sky boxes.

    Attributes:
        host (str): The IP address of the Sky box.
        port (int): The port to connect to the Sky box.
        box_model (str): The model of the Sky box.
        delay_commands (float): The delay in seconds between sending commands in a sequence (default: 0.01).
        wait_power_toggle (float): The wait time in seconds after toggling the power state (default: 1.0).
        key_map (dict): The names of keys mapped to their command codes.
        power_state_upnp_uri (str): The URI to a path used to determine the power state of the box over UPNP.
    """

    def __init__(
        self,
        host: str,
        port: int = 49160,
        upnp_port: int = 49159,
        box_model: str = "skyhd",
        delay_commands: float = 0.01,
        wait_power_toggle: float = 3.0,
    ) -> None:
        """
        Initialize the RemoteControl instance.

        Args:
            host (str): IP address of the Sky box.
            port (int): Port for connection (default: 49160).
            upnp_port (int): Port for UPNP connection (default: 49159).
            box_model (str): Model of the Sky box (default: "skyhd").
            delay_commands (float): The delay in seconds between sending commands in a sequence (default: 0.01).
            wait_power_toggle (float): The wait time in seconds after toggling the power state (default: 1.0).

        Raises:
            ValueError: If the provided box_model is not supported.
        """
        self.host = host
        self.port = port
        self.upnp_port = upnp_port
        self.box_model = box_model.lower()
        self.delay_commands = delay_commands
        self.wait_power_toggle = wait_power_toggle

        if self.box_model not in BOX_MODEL_DEFINITIONS:
            raise ValueError(
                f"Unsupported box model '{box_model}'. Supported box models: {', '.join(BOX_MODEL_DEFINITIONS)}"
            )

        self.key_map = BOX_MODEL_DEFINITIONS[self.box_model]["key_map"]
        self.power_state_upnp_uri = BOX_MODEL_DEFINITIONS[self.box_model]["power_state_upnp_uri"]

    async def check_connectable(self, timeout: int = 3) -> bool:
        """
        Check if the device is connectable and identify if it is a Sky box.

        This method attempts to open a connection to the Sky box on the specified port
        and validates the response. A payload test (`b"4100002240"`) is recommended
        for better accuracy but has only been tested on SkyHD models.

        Args:
            timeout (int): Maximum time in seconds to wait for the connection (default: 3).

        Returns:
            bool: True if the device is connectable and identified as a Sky box.

        Raises:
            ConnectionTimeoutError: If the connection attempt times out.
            SkyBoxConnectionError: If the connection fails.
            NotASkyBoxError: If the connected device is not identified as a Sky box.
        """
        connection_future = asyncio.open_connection(self.host, self.port)
        try:
            reader, writer = await asyncio.wait_for(connection_future, timeout)
        except asyncio.TimeoutError as e:
            raise ConnectionTimeoutError from e
        except OSError as e:
            raise SkyBoxConnectionError from e
        try:
            data = await asyncio.wait_for(reader.read(3), timeout)
        except asyncio.TimeoutError as e:
            raise NotASkyBoxError from e
        if data != bytes("SKY", "ascii"):
            raise NotASkyBoxError

        writer.close()
        await writer.wait_closed()
        return True

    def get_power_state(self) -> str:
        """
        Check the current power state of the Sky box.

        For SkyHD boxes, this method uses a UPnP request to determine the power state
        by sending a GET request to a predefined URI. SkyQ support is possible but
        not yet implemented or tested.

        Credit:
            This technique is inspired by contributions from C4rtm4N on the Domoticz forums:
            https://forum.domoticz.com/viewtopic.php?t=10380&start=22.

        Returns:
            str: 'on' if the Sky box is powered on, 'off' if it is powered off.

        Raises:
            SkyBoxConnectionError: If the connection fails or the power state cannot be determined.
            NotImplementedError: If the power state check is not implemented for the current box model.
        """
        if self.box_model == "skyhd":
            conn = None
            try:
                conn = http.client.HTTPConnection(self.host, self.upnp_port, timeout=5)
                conn.request("GET", self.power_state_upnp_uri)
                response = conn.getresponse()

                if response.status == http.HTTPStatus.OK:
                    return "on"
                elif response.status == http.HTTPStatus.NOT_FOUND:
                    return "off"
                else:
                    raise Exception(f"Unexpected response: {response.status} {response.reason}")
            except (http.client.HTTPException, socket.error) as e:
                raise SkyBoxConnectionError(f"Failed to get power status: {e}") from e
            finally:
                if conn:
                    conn.close()

        # TODO implement once SkyQ has been tested.
        # elif self.box_model =="skyq":

        else:
            raise NotImplementedError(f"Getting the power state for {self.box_model} box models is not implemented!")

    def set_power_state(self, desired_state: str) -> None:
        """
        Set the power state of the Sky box.

        This method sends the appropriate power command if the current state does not match.

        Args:
            desired_state (str): Desired state of the Sky box, "on" or "off".

        Raises:
            ValueError: If the desired_state is not "on" or "off".
            NotImplementedError: If the box model does not support power state changes.

        Note:
            If the desired state matches the current state, no command is sent.
        """
        if desired_state not in ("on", "off"):
            raise ValueError("Invalid desired_state. Use 'on' or 'off'.")

        current_state = self.get_power_state()

        if desired_state == current_state:
            logger.debug("Sky box is already %s. No command sent.", current_state)
            return

        command = "power"
        logger.debug("Sending command '%s' to change state from %s to %s.", command, current_state, desired_state)
        self.send_keys(command)
        time.sleep(self.wait_power_toggle)

    def send_keys(self, key_list):
        """Send a single key or list of keys to the Sky box."""
        if isinstance(key_list, list):
            for item in key_list:
                if item not in self.key_map:
                    raise ValueError(f"Invalid key: {item}")
                self._send_key(item)
                time.sleep(self.delay_commands)
        elif key_list not in self.key_map:
            raise ValueError(f"Invalid key: {key_list}")
        else:
            self._send_key(key_list)

    def _send_key(self, key: str) -> None:
        """Open a connection to the Sky box and send a key command."""
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
