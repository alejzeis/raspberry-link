from time import sleep
import dbus
import dbus.mainloop.glib
import logging
import subprocess


class DummyHandsfreeManager:
    def __init__(self):
        pass

    def on_device_connected(self, name, address, signal_strength):
        pass

    def on_device_disconnected(self, name, address):
        pass

    def answer_call(self, path):
        pass

    def hangup_call(self, path):
        pass

    def poll(self):
        pass

    def dial_call(self, path):
        pass

    def music_play(self):
        pass

    def music_pause(self):
        pass

    def music_skip(self):
        pass

    def music_back(self):
        pass


class HandsfreeManager(DummyHandsfreeManager):
    bus = None
    manager = None
    modems = None

    audio_manager = None
    bluez_mediaplayer = None

    track_info = {
        "status": "Unknown",
        "title": "Unknown",
        "artist": "Unknown",
        "album": "Unknown"
    }
    calls = {}

    logger = logging.getLogger("RL-HandsfreeManager")

    active_calls = 0

    def __init__(self, audio_manager):
        super().__init__()
        self.audio_manager = audio_manager

        self.logger.setLevel(logging.INFO)

        self.bus = dbus.SystemBus()
        self.manager = dbus.Interface(self.bus.get_object('org.ofono', '/'), 'org.ofono.Manager')
        self.bus.add_signal_receiver(
            self._on_bluealsa_pcm_added,
            bus_name='org.bluealsa',
            signal_name='PCMAdded'
        )
        self.bus.add_signal_receiver(
            self._on_dbus_mediaplayer_property_changed,
            bus_name='org.bluez',
            signal_name='PropertiesChanged',
            dbus_interface='org.bluez.MediaPlayer1',
            path_keyword='path'
        )

        self.modems = self.manager.GetModems()

        for modem, props in self.modems:
            self.logger.info("Auto-detected Previous Modem: " + str(modem))

    # Callback for DBus to detect when the current track information changes
    def _on_dbus_mediaplayer_property_changed(self, property_name, value, path):
        player = dbus.Interface(self.bus.get_object("org.bluez", path), "org.bluez.MediaPlayer1")
        properties = player.GetProperties()

        if property_name == "Status" or property_name == "Track":
            self.track_info["status"] = properties["Status"]
            self.track_info["title"] = properties["Track"].get('Title', '')
            self.track_info["artist"] = properties["Track"].get('Artist', '')
            self.track_info["album"] = properties["Track"].get('Album', '')

    def _set_bluealsa_volume(self, type, numid, value):
        if subprocess.run(['amixer', '-D', 'bluealsa', 'cset', 'numid=' + str(numid), value + "%"]).returncode != 0:
            self.logger.warning("Nonzero exit code while setting " + type + " volume")

    # Callback for DBus to detect when to set the volumes for A2DP and SCO
    def _on_bluealsa_pcm_added(self, path, properties):
        # Set the A2DP and SCO volumes
        self._set_bluealsa_volume("A2DP", 2, self.audio_manager.config['audio']['a2dp-volume'])
        self._set_bluealsa_volume("SCO playback", 6, self.audio_manager.config['audio']['sco-volume-send'])
        self._set_bluealsa_volume("SCO capture", 4, self.audio_manager.config['audio']['sco-volume-receive'])

    def on_device_connected(self, name, address, strength):
        # Obtain MediaPlayer interface from DBUS so we can get track information
        obj = self.bus.get_object('org.bluez', "/")
        mgr = dbus.Interface(obj, 'org.freedesktop.DBus.ObjectManager')
        for path, ifaces in mgr.GetManagedObjects().items():
            if 'org.bluez.MediaPlayer1' in ifaces:
                self.bluez_mediaplayer = dbus.Interface(
                    self.bus.get_object('org.bluez', path),
                    'org.bluez.MediaPlayer1')
        if not self.bluez_mediaplayer:
            self.logger.warning("Failed to find MediaPlayer Dbus interface for BT device: " + address)

    def on_device_disconnected(self, name, address):
        self.bluez_mediaplayer = None

    def poll(self):
        self.modems = self.manager.GetModems()  # Update list in case of new modems from newly-paired devices

        for modem, modem_props in self.modems:
            if "org.ofono.VoiceCallManager" not in modem_props["Interfaces"]:
                continue

            mgr = dbus.Interface(self.bus.get_object('org.ofono', modem), 'org.ofono.VoiceCallManager')

            calls = mgr.GetCalls()

            for path, properties in calls:
                state = properties['State']
                name = properties['Name']
                line_ident = properties['LineIdentification']

                if state != "disconnected":
                    self.calls[line_ident] = {
                        "state": state,
                        "name": name,
                        "modem": modem
                    }
                else:
                    del self.calls[line_ident]

            if len(self.calls) > 0:
                self.audio_manager.on_call_active()

    def answer_call(self, path):
        call = dbus.Interface(self.bus.get_object('org.ofono', path), 'org.ofono.VoiceCall')
        if call:
            call.Answer()
            self.logger.info("Answered call: " + path)
            return True
        else:
            return False

    def hangup_call(self, path):
        call = dbus.Interface(self.bus.get_object('org.ofono', path), 'org.ofono.VoiceCall')
        if call:
            call.Hangup()
            self.logger.info("Hung up on call: " + path)
            return True
        else:
            return False

    def music_play(self):
        if self.bluez_mediaplayer is not None:
            self.bluez_mediaplayer.Play()

    def music_pause(self):
        if self.bluez_mediaplayer is not None:
            self.bluez_mediaplayer.Pause()

    def music_skip(self):
        if self.bluez_mediaplayer is not None:
            self.bluez_mediaplayer.Next()

    def music_back(self):
        if self.bluez_mediaplayer is not None:
            self.bluez_mediaplayer.Previous()
