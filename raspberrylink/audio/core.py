from subprocess import run
from threading import Thread
from time import sleep

import atexit
import logging

import dbus
import dbus.mainloop.glib

from raspberrylink.audio import handsfree, routing


logger = logging.getLogger("RL-Audio")
logger.setLevel(logging.INFO)


class AudioManager:
    handsfree_mgr = None

    router = None
    config = None

    connected_device = {
        "connected": False,
        "name": "Unknown",
        "address": "",
        "signal_strength": 0
    }
    call_audio_routing_begun = False

    bus = None

    poll_thread = None

    def __init__(self, conf):
        self.config = conf
        self.handsfree_mgr = handsfree.HandsfreeManager(self)

        self.router = routing.PhysicalAudioRouter(self)

        self.bus = dbus.SystemBus()
        self.bus.add_signal_receiver(
            self._on_dbus_device_property_changed,
            bus_name='org.bluez',
            signal_name='PropertiesChanged',
            dbus_interface='org.freedesktop.DBus.Properties',
            path_keyword='path'
        )

        atexit.register(self._exit_handler)

        self.poll_thread = Thread(target=self._poll, daemon=True)
        self.poll_thread.start()

    def _exit_handler(self):
        self.router.on_stop_media_playback()
        self.router.on_end_call()

    def _poll(self):
        logger.info("Starting Polling Thread")
        while True:
            self.handsfree_mgr.poll()
            sleep(1)

    def _on_dbus_device_property_changed(self, interface, changed, invalidated, path):
        if interface == "org.bluez.Device1":
            device = dbus.Interface(self.bus.get_object("org.bluez", path), "org.bluez.Device1")
            properties = dbus.Interface(device, "org.freedesktop.DBus.Properties")

            if properties.Get("org.bluez.Device1", "Connected"):
                name = properties.Get("org.bluez.Device1", "Name")
                address = properties.Get("org.bluez.Device1", "Address")
                rssi = properties.Get("org.bluez.Device1", "RSSI")

                logger.info("Device connected: " + name + " with address " + address)
                self.connected_device = {
                    "connected": True,
                    "name": name,
                    "address": address,
                    "signal_strength": rssi
                }

                self.router.on_start_media_playback()
                self.handsfree_mgr.on_device_connected(name, address, rssi)

                # Save bluetooth address to try to automatically reconnect on next startup
                f = open('/var/cache/raspberrylink-last-device', 'w')
                f.write(address)
                f.close()
            else:
                name = properties.Get("org.bluez.Device1", "Name")
                address = properties.Get("org.bluez.Device1", "Address")

                logger.info("Device disconnected: " + name + " with address " + address)
                self.connected_device = {
                    "connected": False,
                    "name": "Unknown",
                    "address": "",
                    "signal_strength": 0
                }

                self.router.on_stop_media_playback()
                self.handsfree_mgr.on_device_disconnected(name, address)
                self.call_audio_routing_begun = False
                self.router.on_end_call()

        self.handsfree_mgr.on_dbus_bluez_property_changed(interface, changed, invalidated)

    # Called by the Handsfree manager when there is an active call
    def on_call_active(self):
        # check to make sure we haven't already started routing call audio for the device
        if self.call_audio_routing_begun:
            return

        # start routing call audio
        self.router.on_start_call()
        self.call_audio_routing_begun = True


def attempt_reconnect(conf):
    adapter_address = conf["audio"]["bt-adapter-address"]

    if adapter_address != "00:00:00:00:00:00":
        prefix = "MULTIPLE_ADAPTERS=1 BT_ADAPTER_ADDR=" + adapter_address
    else:
        prefix = "MULTIPLE_ADAPTERS=0 "

    run(prefix + " /opt/raspberrylink/raspilink-bt-reconnect", shell=True)


# Entry function for raspilink-audio
def bootstrap(conf):
    if not conf['audio'].getboolean("enabled"):
        logger.error("Audio support not enabled in RaspberryLink Server config.")
        return

    name = conf['audio']['bt-name']
    adapter_address = conf['audio']['bt-adapter-address']
    volume = conf['audio']['physical-output-volume'] + "%"
    mixer_numid = conf['audio']['mixer-numid-output']
    mic_mixer_numid = conf['audio']['mixer-numid-input']
    mic_volume = conf['audio']['physical-input-volume'] + "%"

    cmd = "BT_DEVICE_NAME=" + name + " SYSTEM_VOLUME=" + volume \
          + " MIXER_NUMID=" + mixer_numid + " MIC_MIXER_NUMID=" + mic_mixer_numid \
          + " MICROPHONE_VOLUME=" + mic_volume \
          + " /opt/raspberrylink/raspilink-bt-init"

    if adapter_address != "00:00:00:00:00:00":
        cmd = "MULTIPLE_ADAPTERS=1 BT_ADAPTER_ADDR=" + adapter_address + " " + cmd
    else:
        cmd = "MULTIPLE_ADAPTERS=0 " + cmd

    logger.info("Running audio bootstrap script: " + cmd)
    run(cmd, shell=True)

    return AudioManager(conf)
