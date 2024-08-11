# skyboxremote
Python library to send commands to a Sky HD box
Based on the (sky-remote NodeJS)[https://github.com/dalhundal/sky-remote/] module from dalhundal
#### Installation
`pip install skyboxremote`

## Usage
Pass ip and port into RemoteControl function to create a remote.
Port defaults to 49160 for SkyHD or SkyQ, set to port 5900 for legacy SkyQ firmware < 060
Time between commands in a sequence defaults to 0.01s.
#### Example
```python
from skyboxremote import RemoteControl

remote = RemoteControl('192.168.1.60')

# Send a single command
remote.send_keys('sky')

# Send a sequence of commands
remote.send_keys(['channelup', 'record', 'select'])
```

### Available remote control commands
"power"

"sky"

"tvguide" "boxoffice" "services" "interactive"

"up" "down" "left" "right"

"select" "backup"

"channelup" "channeldown"

"i" "text" "help"

"red" "green" "yellow" "blue"

"0" "1" "2" "3" "4" "5" "6" "7" "8" "9"

"play" "pause" "stop" "record" "fastforward" "rewind"

"sidebar"
"dismiss"
"search"
"home"







