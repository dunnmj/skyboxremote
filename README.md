# skyboxremote
Python library to send commands to a Sky HD box.
Based on the [sky-remote NodeJS](https://github.com/dalhundal/sky-remote/) module from dalhundal.

## Installation
`pip install skyboxremote`

## Usage
Pass the IP of your Sky box into the `RemoteControl` class to create a remote.

- `host` (_required_)
  - The IP address of the Sky box.
- `port` (_optional_)
  - The port which the Sky box receives commands on.
  - Default is `49160` for SkyHD or SkyQ.
  - For legacy SkyQ firmware (versions < 060), set the port to `5900`.
- `upnp_port` (_optional_)
  - The port on which the Sky box handles UPNP.
  - Default is `49159`.
- `box_model` (_optional_)
  - The model of the Sky box, either `skyhd` or `skyq`.
  - Default is `skyhd`.
  - The model type is used to determine what commands are available and how to manage the power of the Sky box.
  - A full list of `skyhd` models is available [here](https://en.wikipedia.org/wiki/Sky%2B_HD).
- `delay_commands` (_optional_)
  - The delay in seconds between sending commands in a sequence.
  - Default is `0.01` seconds.
- `wait_power_toggle` (_optional_)
  - The wait time in seconds after toggling the power state, using `set_power_state`.
  - Default is `3.00` seconds.

### Example
```python
from skyboxremote import RemoteControl

remote = RemoteControl('192.168.1.60')

# Send a single command
remote.send_keys('sky')

# Send a sequence of commands
remote.send_keys(['sky', 'tvguide', 'green'])
```

### Verbose example
```python
from skyboxremote import RemoteControl

remote = RemoteControl(
    host='192.168.0.90',
    port=49160,
    upnp_port=49159,
    box_model='skyhd',
    delay_commands=0.01,
    wait_power_toggle=3.00
)

# Send a single command
remote.send_keys('sky')

# Send a sequence of commands
remote.send_keys(['sky', 'tvguide', 'green'])

# Returns either "on" or "off"
remote.get_power_state()

# Powers the box either "on" or "off", after first checking if the box is already "on"/"off"
remote.set_power_state("on")
```

### Available remote control commands
`power`

`sky`

`tvguide` `boxoffice` `services` `interactive`

`up` `down` `left` `right`

`select` `backup`

`channelup` `channeldown`

`i` `text` `help`

`red` `green` `yellow` `blue`

`0` `1` `2` `3` `4` `5` `6` `7` `8` `9`

`play` `pause` `stop` `record` `fastforward` `rewind`

`sidebar`
`dismiss`
`search`
`home`
