import os
import dbus
import dbus.mainloop.glib
import logging
import subprocess


class DummyHandsfreeManager:
    def __init__(self):
        pass

    def on_dbus_bluez_property_changed(self, interface, changed, invalidated):
        pass

    def on_device_connected(self, name, address, signal_strength):
        pass

    def on_device_disconnected(self, name, address):
        pass

    def answer_call(self, path):
        pass

    def hangup_call(self, path):
        pass

    def hangup_all(self):
        pass

    def dial_call(self, number):
        pass

    def poll(self):
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

        if os.getenv("RASPILINK_DEBUG") == "1":
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

        self.bus = dbus.SystemBus()
        self.bus.add_signal_receiver(
            self._on_bluealsa_pcm_added,
            bus_name='org.bluealsa',
            signal_name='PCMAdded'
        )

        if audio_manager.call_support:
            self.manager = dbus.Interface(self.bus.get_object('org.ofono', '/'), 'org.ofono.Manager')
            self.modems = self.manager.GetModems()

            for modem, props in self.modems:
                self.logger.debug("Found Modem: " + str(modem))

    # Callback for DBus to detect when the current track information changes
    def on_dbus_bluez_property_changed(self, interface, changed, invalidated):
        if interface != 'org.bluez.MediaPlayer1':
            return
        for prop, value in changed.items():
            if prop == 'Status':
                self.track_info['status'] = str(value)
            elif prop == 'Track':
                self.track_info["title"] = value.get("Title", "")
                self.track_info["artist"] = value.get("Artist", "")
                self.track_info["album"] = value.get("Album", "")

        if not self.bluez_mediaplayer:
            # Try to find the MediaPlayer instance since we don't have it.
            self._obtain_bluez_mediaplayer()

    def _set_bluealsa_volume(self, type, numid, value):
        if subprocess.run(['amixer', '-D', 'bluealsa', 'cset', 'numid=' + str(numid), value + "%"], capture_output=True).returncode != 0:
            self.logger.warning("Nonzero exit code while setting " + type + " volume")

    def _obtain_bluez_mediaplayer(self):
        # Obtain MediaPlayer interface from DBUS so we can get track information
        obj = self.bus.get_object('org.bluez', "/")
        mgr = dbus.Interface(obj, 'org.freedesktop.DBus.ObjectManager')
        for path, ifaces in mgr.GetManagedObjects().items():
            if 'org.bluez.MediaPlayer1' in ifaces:
                self.bluez_mediaplayer = dbus.Interface(
                    self.bus.get_object('org.bluez', path),
                    'org.bluez.MediaPlayer1')

                self.logger.info("Obtained MediaPlayer DBus Interface")
                break

        if not self.bluez_mediaplayer:
            self.logger.warning("Failed to find MediaPlayer Dbus interface")

    # Callback for DBus to detect when to set the volumes for A2DP and SCO
    def _on_bluealsa_pcm_added(self, path, properties):
        self.set_volumes()

    def set_volumes(self):
        # Set the A2DP and SCO volumes
        self._set_bluealsa_volume("A2DP", 2, self.audio_manager.config['audio']['a2dp-volume'])
        self._set_bluealsa_volume("SCO playback", 6, self.audio_manager.config['audio']['sco-volume-send'])
        self._set_bluealsa_volume("SCO capture", 4, self.audio_manager.config['audio']['sco-volume-receive'])

    def on_device_connected(self, name, address, strength):
        self._obtain_bluez_mediaplayer()

    def on_device_disconnected(self, name, address):
        self.bluez_mediaplayer = None
        self.calls = {}
        self.track_info = {
            "status": "Unknown",
            "title": "Unknown",
            "artist": "Unknown",
            "album": "Unknown"
        }

    def poll(self):
        self.modems = self.manager.GetModems()  # Update list in case of new modems from newly-paired devices

        for modem, modem_props in self.modems:
            if "org.ofono.VoiceCallManager" not in modem_props["Interfaces"]:
                continue

            mgr = dbus.Interface(self.bus.get_object('org.ofono', modem), 'org.ofono.VoiceCallManager')

            calls = mgr.GetCalls()

            # Due to polling we aren't able to catch when calls end up disconnecting, so we just overwrite the list
            # each time.
            currentcalls = {}
            for path, properties in calls:
                state = properties['State']
                name = properties['Name']
                line_ident = properties['LineIdentification']

                if state != "disconnected":
                    currentcalls[line_ident] = {
                        "path": path,
                        "state": state,
                        "name": name,
                        "modem": modem
                    }

            self.calls = currentcalls
            if len(self.calls) > 0:
                self.audio_manager.on_call_active()

    def answer_call(self, path):
        call = dbus.Interface(self.bus.get_object('org.ofono', path), 'org.ofono.VoiceCall')
        if call:
            call.Answer()
            self.logger.debug("Answered call: " + path)
            return True
        else:
            return False

    def hangup_call(self, path):
        call = dbus.Interface(self.bus.get_object('org.ofono', path), 'org.ofono.VoiceCall')
        if call:
            call.Hangup()
            self.logger.debug("Hung up on call: " + path)
            return True
        else:
            return False

    def hangup_all(self):
        vcm = dbus.Interface(self.bus.get_object("org.ofono", self.modems[0][0]), "org.ofono.VoiceCallManager")
        vcm.HangupAll()
        self.logger.debug("Hungup on all calls for " + self.modems[0][0])

    def dial_call(self, number):
        vcm = dbus.Interface(self.bus.get_object("org.ofono", self.modems[0][0]), "org.ofono.VoiceCallManager")
        vcm.Dial(number, "default")
        self.logger.debug("Dialed number " + number + " on " + self.modems[0][0])

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
