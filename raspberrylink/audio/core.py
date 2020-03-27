from subprocess import run
from threading import Thread
from socket import socket, AF_UNIX, SOCK_STREAM
from sys import exit

import atexit
import logging

from gi.repository import GLib
import dbus
import dbus.mainloop.glib

from raspberrylink import config
from raspberrylink.audio import handsfree, routing


logger = logging.getLogger("RL-Audio")
logger.setLevel(logging.INFO)


class AudioManager:
    handsfree_mgr = None

    sock = None
    active_connection = None
    recv_thread = None

    call_support = False
    router = None
    config = None

    def __init__(self, conf, socket_file="/run/raspberrylink_audio.socket"):
        self.config = conf
        self.call_support = conf['audio'].getboolean("handsfree-enabled")
        if self.call_support:
            self.handsfree_mgr = handsfree.HandsfreeManager(self)
        else:
            self.handsfree_mgr = handsfree.DummyHandsfreeManager()

        self.sock = socket(AF_UNIX, SOCK_STREAM)
        self.sock.bind(socket_file)

        self.router = routing.PhysicalAudioRouter(self)
        self.router.on_start_media_playback()  # Immediately begin playing any A2DP data

        atexit.register(self._exit_handler)

        self.recv_thread = Thread(target=self._recv_data, daemon=True)
        self.recv_thread.start()

    def _exit_handler(self):
        if self.active_connection is not None:
            self.active_connection.close()

        self.sock.close()

        self.router.on_stop_media_playback()
        self.router.on_end_call()

    def _recv_data(self):
        self.sock.listen(1)

        while True:
            self.active_connection, addr = self.sock.accept()

            while True:
                data = self.active_connection.recv(512).decode("UTF-8").split("~")

                if data[0] == "CALL-ANSWER":
                    self.handsfree_mgr.answer_call(data[1])
                    pass
                elif data[0] == "CALL-HANGUP":
                    self.handsfree_mgr.hangup_call(data[1])
                    pass


# Entry function for raspilink-audio
def bootstrap():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    logger.info("Starting RaspberryLink Bluetooth Audio Service")

    conf = config.load_server_config()
    if not conf['audio'].getboolean("enabled"):
        logger.error("Audio support not enabled in RaspberryLink Server config. Exiting")
        exit(1)

    handsfree_support = conf['audio'].getboolean("handsfree-enabled")
    name = conf['audio']['bt-name']
    volume = conf['audio']['output-volume'] + "%"

    logger.info("Running bootstrap script")
    run("HANDSFREE=" + str(int(handsfree_support)) + " BLUETOOTH_DEVICE_NAME=" + name + " SYSTEM_VOLUME=" + volume
        + " raspilink-audio-start", shell=True)

    AudioManager(conf)

    mainloop = GLib.MainLoop()
    mainloop.run()
