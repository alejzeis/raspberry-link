from subprocess import run
from threading import Thread
from socket import socket, AF_UNIX, SOCK_STREAM
from sys import exit
from os import remove
from time import sleep

import atexit
import logging
import queue

from gi.repository import GLib
import dbus
import dbus.mainloop.glib

from raspberrylink import config, util
from raspberrylink.audio import handsfree


logger = logging.getLogger("RL-Audio")
logger.setLevel(logging.INFO)


class AudioManager:
    handsfree_mgr = None

    socket_file = ""
    sock = None
    socket_send_queue = None
    active_socket_connection = None
    recv_thread = None
    poll_thread = None

    config = None

    device_connected = False

    def __init__(self, conf, socket_file="/run/raspberrylink_audio.socket"):
        self.config = conf
        self.socket_file = socket_file
        self.handsfree_mgr = handsfree.HandsfreeManager(self)

        self.sock = socket(AF_UNIX, SOCK_STREAM)
        self.sock.bind(socket_file)
        logger.debug("Bound socket to " + socket_file)
        self.socket_send_queue = queue.Queue()

        atexit.register(self._exit_handler)

        self.recv_thread = Thread(target=self._recv_data, daemon=True)
        self.recv_thread.start()

        self.poll_thread = Thread(target=self._poll, daemon=True)
        self.poll_thread.start()

    def _exit_handler(self):
        if self.active_socket_connection is not None:
            self.active_socket_connection.close()

        self.sock.close()

        remove(self.socket_file)  # Closing the socket doesn't actually delete the file

    def _poll(self):
        logger.info("Starting Polling Thread")
        while True:
            self._poll_connections()
            self.handsfree_mgr.poll()

            sleep(0.5)

    def _poll_connections(self):
        # Check if a device has connected recently, and then start media playback or end it
        new_status = util.get_device_connected()
        if not self.device_connected and new_status[0]:
            # Save bluetooth address to try to automatically reconnect on next startup
            f = open('/var/cache/bluetooth/reconnect_device', 'w')
            f.write(new_status[1])
            f.close()
            logger.info("Device connected: " + new_status[1])
        elif self.device_connected and not new_status[0]:
            logger.info("Device disconnected: " + new_status[1])

        self.device_connected = new_status[0]

    def _recv_data(self):
        logger.info("Started Socket Receive thread")
        self.sock.listen(1)

        while True:
            self.active_socket_connection, addr = self.sock.accept()
            logger.debug("Accepted socket connection")
            self.active_socket_connection.setblocking(False)

            while True:
                # Check if the connection was closed
                if self.active_socket_connection.fileno() == -1:
                    break

                try:
                    raw = self.active_socket_connection.recv(512)
                    if len(raw) > 1:
                        data = raw.decode("UTF-8").split("~")

                        if data[0] == "CALL-ANSWER":
                            # Answer the specified call
                            self.handsfree_mgr.answer_call(data[1])
                            pass
                        elif data[0] == "CALL-HANGUP":
                            # Hangup the specified call
                            self.handsfree_mgr.hangup_call(data[1])
                            pass
                except BlockingIOError:
                    pass

                if not self.socket_send_queue.empty():
                    self.active_socket_connection.send(self.socket_send_queue.get())

                sleep(0.2)


# Entry function for raspilink-audio
def bootstrap():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    logger.info("Starting RaspberryLink Bluetooth Audio Service...")

    conf = config.load_server_config()

    name = conf['audio']['bt-name']
    adapter_address = conf['audio']['bt-adapter-address']
    volume = conf['audio']['output-volume'] + "%"
    mixer_numid = conf['audio']['mixer-numid-output']
    mic_mixer_numid = conf['audio']['mixer-numid-input']
    mic_volume = conf['audio']['input-volume'] + "%"

    cmd = "BLUETOOTH_DEVICE_NAME=" + name + " SYSTEM_VOLUME=" + volume \
          + " MIXER_NUMID=" + mixer_numid + " MIC_MIXER_NUMID=" + mic_mixer_numid \
          + " MICROPHONE_VOLUME=" + mic_volume + " /usr/src/raspberrylink/raspilink-audio-start"

    if adapter_address != "00:00:00:00:00:00":
        cmd = "MULTIPLE_ADAPTERS=1 BT_ADAPTER_ADDR=" + adapter_address + " " + cmd
    else:
        cmd = "MULTIPLE_ADAPTERS=0 " + cmd

    logger.info("Running bootstrap script: " + cmd)
    run(cmd, shell=True)

    AudioManager(conf)

    logger.info("Done! Starting GLib Main Loop.")

    mainloop = GLib.MainLoop()
    mainloop.run()
