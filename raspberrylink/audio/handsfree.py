from time import sleep
import dbus
import dbus.mainloop.glib
import logging
import subprocess


class DummyHandsfreeManager:
    def __init__(self):
        pass

    def on_device_connected(self, address):
        pass

    def on_device_disconnected(self, address):
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

    logger = logging.getLogger("RL-HandsfreeManager")

    active_calls = 0

    def __init__(self, audio_manager):
        super().__init__()
        self.audio_manager = audio_manager

        self.logger.setLevel(logging.INFO)

        self.bus = dbus.SystemBus()
        self.manager = dbus.Interface(self.bus.get_object('org.ofono', '/'), 'org.ofono.Manager')
        self.bus.add_signal_receiver(
            self._on_pcm_added,
            bus_name='org.bluealsa',
            signal_name='PCMAdded'
        )
        self.bus.add_signal_receiver(
            self._on_dbus_property_changed,
            bus_name='org.bluez',
            signal_name='PropertiesChanged',
            dbus_interface='org.freedesktop.DBus.Properties')

        self.modems = self.manager.GetModems()

        for modem, props in self.modems:
            self.logger.info("Auto-detected Previous Modem: " + str(modem))

    # Callback for DBus to detect when the current track information changes
    def _on_dbus_property_changed(self, interface, changed, invalidated):
        if interface != 'org.bluez.MediaPlayer1':
            return
        for prop, value in changed.items():
            if prop == 'Status':
                self.audio_manager.socket_send_queue.put(("PLAYBACK-STATUS~" + str(value)).encode("UTF-8"))
            elif prop == 'Track':
                self.audio_manager.socket_send_queue.put(("PLAYBACK-INFO~" + value.get('Title', '')
                                                          + "~" + value.get('Artist', '') + "~"
                                                          + value.get('Album', '')).encode("UTF-8"))

    def _set_bluealsa_volume(self, type, numid, value):
        if subprocess.run(['amixer', '-D', 'bluealsa', 'cset', 'numid=' + str(numid), value + "%"]).returncode != 0:
            self.logger.warning("Nonzero exit code while setting " + type + " volume")

    # Callback for DBus to detect when to set the volumes for A2DP and SCO
    def _on_pcm_added(self, address):
        # Set the A2DP and SCO volumes
        self._set_bluealsa_volume("A2DP", 2, self.audio_manager.config['audio']['a2dp-volume'])
        self._set_bluealsa_volume("SCO playback", 6, self.audio_manager.config['audio']['sco-volume-send'])
        self._set_bluealsa_volume("SCO capture", 4, self.audio_manager.config['audio']['sco-volume-receive'])

    def on_device_connected(self, address):
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

    def on_device_disconnected(self, address):
        self.bluez_mediaplayer = None

    def poll(self):
        self.modems = self.manager.GetModems()  # Update list in case of new modems from newly-paired devices

        call_count = 0
        calls_data = ""
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
                    call_count += 1
                else:
                    call_count -= 1

                if self.audio_manager.active_socket_connection is not None:
                    calls_data += (modem + "`" + state + "`" + name + "`" + line_ident + "|")

        self.active_calls = call_count

        # Send our current Call List to the main Server process
        if self.audio_manager.active_socket_connection is not None and calls_data != "":
            self.audio_manager.on_call_active()
            self.audio_manager.socket_send_queue.put(("CALLS-LIST~" + calls_data).encode("UTF-8"))

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

