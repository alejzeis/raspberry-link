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
from raspberrylink.audio import handsfree, routing


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

    call_support = False
    router = None
    config = None

    device_connected = False
    call_audio_routing_begun = False

    def __init__(self, conf, socket_file="/run/raspberrylink_audio.socket"):
        self.config = conf
        self.socket_file = socket_file
        self.call_support = conf['audio'].getboolean("handsfree-enabled")
        if self.call_support:
            logger.warning("Experimental handsfree support is enabled. This feature may not work as well as intended"
                           ", or may not work at all.")
            self.handsfree_mgr = handsfree.HandsfreeManager(self)
        else:
            self.handsfree_mgr = handsfree.DummyHandsfreeManager()

        self.sock = socket(AF_UNIX, SOCK_STREAM)
        self.sock.bind(socket_file)
        logger.debug("Bound socket to " + socket_file)
        self.socket_send_queue = queue.Queue()

        self.router = routing.PhysicalAudioRouter(self)

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

        self.router.on_stop_media_playback()
        self.router.on_end_call()

    def _poll(self):
        logger.info("Starting Polling Thread")
        while True:
            self._poll_connections()
            if self.call_support:
                self.handsfree_mgr.poll()

            sleep(0.5)

    def _poll_connections(self):
        # Check if a device has connected recently, and then start media playback or end it
        new_status = util.get_device_connected()
        if not self.device_connected and new_status[0]:
            self.router.on_start_media_playback()
            self.handsfree_mgr.on_device_connected(new_status[1])

            # Save bluetooth address to try to automatically reconnect on next startup
            f = open('/var/cache/bluetooth/reconnect_device', 'w')
            f.write(new_status[1])
            f.close()
        elif self.device_connected and not new_status[0]:
            self.router.on_stop_media_playback()
            self.handsfree_mgr.on_device_disconnected(new_status[1])
            if self.call_support:  # Stop call audio routing if supported
                # Reset call audio routing variable since we don't have a device connected anymore
                self.call_audio_routing_begun = False
                self.router.on_end_call()

        self.device_connected = new_status[0]

    # Called by the Handsfree manager when there is an active call
    def on_call_active(self):
        # check to make sure we haven't already started routing call audio for the device
        if not self.call_support or self.call_audio_routing_begun:
            return

        # start routing call audio
        self.router.on_start_call()
        self.call_audio_routing_begun = True

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
                    logger.info("Socket connection closed.")
                    break

                try:
                    raw = self.active_socket_connection.recv(512)
                    if len(raw) > 1:
                        data = raw.decode("UTF-8").split("~")

                        if data[0] == "CALL-ANSWER":
                            # Answer the specified call
                            self.handsfree_mgr.answer_call(data[1])
                        elif data[0] == "CALL-HANGUP":
                            # Hangup the specified call
                            self.handsfree_mgr.hangup_call(data[1])
                        elif data[0] == "MEDIA-PLAY":
                            self.handsfree_mgr.music_play()
                        elif data[0] == "MEDIA-PAUSE":
                            self.handsfree_mgr.music_pause()

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
    if not conf['audio'].getboolean("enabled"):
        logger.error("Audio support not enabled in RaspberryLink Server config. Exiting")
        exit(1)

    handsfree_support = conf['audio'].getboolean("handsfree-enabled")
    name = conf['audio']['bt-name']
    adapter_address = conf['audio']['bt-adapter-address']
    volume = conf['audio']['physical-output-volume'] + "%"
    mixer_numid = conf['audio']['mixer-numid-output']
    mic_mixer_numid = conf['audio']['mixer-numid-input']
    mic_volume = conf['audio']['physical-input-volume'] + "%"
    a2dp_volume = conf['audio']['a2dp-volume'] + "%"
    sco_volume_send = conf['audio']['sco-volume-send'] + "%"
    sco_volume_recv = conf['audio']['sco-volume-receive'] + "%"

    cmd = "HANDSFREE=" + str(int(handsfree_support)) + " BLUETOOTH_DEVICE_NAME=" + name + " SYSTEM_VOLUME=" + volume \
          + " MIXER_NUMID=" + mixer_numid + " MIC_MIXER_NUMID=" + mic_mixer_numid \
          + " MICROPHONE_VOLUME=" + mic_volume \
          + " A2DP_VOLUME=" + a2dp_volume + " SCO_VOLUME_SEND=" + sco_volume_send \
          + " SCO_VOLUME_RECV=" + sco_volume_recv \
          + " /usr/src/raspberrylink/raspilink-audio-start"

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
