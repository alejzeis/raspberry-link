from subprocess import run, Popen, PIPE
from sys import exit
from raspberrylink.server import config


class BTAudioManager:
    handsfree_mgr = None
    pass


# Entry function for raspilink-audio
def bootstrap():
    print("Starting RaspberryLink Bluetooth Audio Service")

    conf = config.load_config()
    if not conf['audio'].getboolean("enabled"):
        print("Audio support not enabled in RaspberryLink Server config. Exiting")
        exit(1)

    handsfree = str(int(conf['audio'].getboolean("handsfree-enabled")))
    name = conf['audio']['bt-name']
    volume = conf['audio']['output-volume']

    print("Running bootstrap script")
    run("HANDSFREE=" + handsfree + " BLUETOOTH_DEVICE_NAME=" + name + " SYSTEM_VOLUME=" + volume
        + " raspilink-audio-start", shell=True)

    # Start APlay instance(s), DBus Main loop?
