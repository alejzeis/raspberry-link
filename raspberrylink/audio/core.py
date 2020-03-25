from subprocess import run, Popen, PIPE
from threading import Thread
from socket import socket, AF_UNIX, SOCK_STREAM
from sys import exit

from gi.repository import GLib
import dbus
import dbus.mainloop.glib

from raspberrylink.server import config
from raspberrylink.audio import handsfree


class BTAudioManager:
    handsfree_mgr = None

    sock = None
    recv_thread = None

    call_support = False
    aplay_a2dp = None
    aplay_sco = None
    aplay_mic = None

    def __init__(self, call_support, socket_file="/run/raspberrylink_audio.socket"):
        self.call_support = call_support
        self.handsfree_mgr = handsfree.HandsfreeManager(self)

        self.sock = socket(AF_UNIX, SOCK_STREAM)
        self.sock.bind(socket_file)

        aplay_a2dp = Popen("bluealsa-aplay --pcm-buffer-time=1000000 00:00:00:00:00:00 --profile-a2dp",
                           stdout=PIPE, stderr=PIPE)
        if call_support:
            aplay_sco = Popen("bluealsa-aplay 00:00:00:00:00:00 --profile-sco", stdout=PIPE, stderr=PIPE)

        self.recv_thread = Thread(target=self._recv_data, daemon=True)
        self.recv_thread.start()

    def _recv_data(self):
        self.sock.listen(1)

        while True:
            con, addr = self.sock.accept()

            while True:
                data = con.recv(512).decode("UTF-8").split("~")

                if data[0] == "CALL-ANSWER":
                    # TODO Answer call
                    pass
                elif data[0] == "CALL-HANGUP":
                    # TODO Hangup Call
                    pass
                else:
                    print("Unknown data from server process")


# Entry function for raspilink-audio
def bootstrap():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    print("Starting RaspberryLink Bluetooth Audio Service")

    conf = config.load_config()
    if not conf['audio'].getboolean("enabled"):
        print("Audio support not enabled in RaspberryLink Server config. Exiting")
        exit(1)

    handsfree_support = conf['audio'].getboolean("handsfree-enabled")
    name = conf['audio']['bt-name']
    volume = conf['audio']['output-volume']

    print("Running bootstrap script")
    run("HANDSFREE=" + str(int(handsfree_support)) + " BLUETOOTH_DEVICE_NAME=" + name + " SYSTEM_VOLUME=" + volume
        + " raspilink-audio-start", shell=True)

    BTAudioManager(handsfree_support)

    mainloop = GLib.MainLoop()
    mainloop.run()
