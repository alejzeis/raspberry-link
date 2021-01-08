from configparser import ConfigParser
from os import getenv
from os.path import exists

default_server_config = """
[server]
; Interface for the WSGI HTTP server to bind on
interface=0.0.0.0
; Port for the WSGI HTTP server to bind to
port=9098

[audio]
; Enable Bluetooth audio support
enabled=yes 

; The Bluetooth device address of the Bluetooth adapter on the Pi
; This is only used if you have multiple adapters, otherwise leave empty
bt-adapter-address=00:00:00:00:00:00

; Bluetooth Name of the Raspberry Pi that will show up when other devices discover and pair to the Pi
bt-name=RaspberryLink

; Percentage from 1-100 (don't include percent sign) to set the actual physical output and input volume of the Pi to
physical-output-volume=20
physical-input-volume=100

; Percentage from 1-100 (don't inclue percent sign) to set the volume of A2DP and SCO playback
; A2DP is used for media and music from the phone, while SCO is strictly for any type of call (phone calls, video calls, VoIP, etc.)
; A2DP is set to 20 here because it's super loud at 100 for some reason. Feel free to tweak.
; SCO Receive volume means the volume from people in the call, whereas send volume is the volume of the user sending their voice to the call.
a2dp-volume=20
sco-volume-receive=100
sco-volume-send=100

; Numid for the Audio Playback and input device (You can find this using "amixer controls", see wiki for more information)
; If this isn't set correctly then volume setting won't work.
; For more information on how to make sure audio goes through the onboard analog port, or using a USB Sound device, see the wiki.
mixer-numid-output=1
mixer-numid-input=0

; The device used as a microphone. (use "arecord --list-devices" to find)  
arecord-device=plughw:1

; ----------------------------------------------------------
; Advanced Configuring of microphone settings for sending call audio to the phone
; ----------------------------------------------------------

; Arguments for capturing audio through microphone, the format and the channels to use.
arecord-format=S16_LE
arecord-sample-rate=16000
arecord-channels=1

; Location of bluealsa-aplay executable to play audio
bluealsa-aplay-exec=/usr/bin/bluealsa-aplay
; Location of the aplay (ALSA) executable
aplay-exec=/usr/bin/aplay
; Location of the arecord (ALSA) executable
arecord-exec=/usr/bin/arecord
"""

default_agent_config = """
[agent]
; Interface for the WSGI HTTP server to bind on
interface=0.0.0.0
; Port for the Agent to listen for commands on
port=9099

; Type of camera this agent has:
; Must be either, rear, front, side, other
type=rear
"""


def load_server_config():
    config_file = getenv("RASPILINK_CONFIG")
    if config_file is None:
        config_file = "/etc/raspberrylink-server.conf"

    if not exists(config_file):
        f = open(config_file, 'w')
        f.writelines(default_server_config)
        f.close()

    config = ConfigParser()
    config.read(config_file)

    return config


def load_agent_config():
    config_location = getenv("RASPILINK_AGENT_CONFIG", "/etc/raspberrylink-agent.conf")

    if not exists(config_location):
        f = open(config_location, 'w')
        f.writelines(default_agent_config)
        f.close()

    config = ConfigParser()
    config.read(config_location)
    return config
