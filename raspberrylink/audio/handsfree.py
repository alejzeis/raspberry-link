from time import sleep
import dbus
import dbus.mainloop.glib
import logging


class DummyHandsfreeManager:
    def __init__(self):
        pass

    def answer_call(self, path):
        pass

    def hangup_call(self, path):
        pass

    def poll(self):
        pass


class HandsfreeManager(DummyHandsfreeManager):
    bus = None
    manager = None
    modems = None

    audio_manager = None

    logger = logging.getLogger("RL-HandsfreeManager")

    active_calls = 0

    def __init__(self, audio_manager):
        super().__init__()
        self.audio_manager = audio_manager

        self.logger.setLevel(logging.INFO)

        self.bus = dbus.SystemBus()
        self.manager = dbus.Interface(self.bus.get_object('org.ofono', '/'), 'org.ofono.Manager')

        self.modems = self.manager.GetModems()

        for modem, props in self.modems:
            self.logger.info("Auto-detected Previous Modem: " + str(modem))

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

                if self.audio_manager.active_connection is not None:
                    calls_data += ("`" + modem + "`" + state + "`" + name + "`" + line_ident + "|")

        self.active_calls = call_count

        # Send our current Call List to the main Server process
        if self.audio_manager.active_socket_connection is not None and calls_data != "":
            # [:-1] to remove redundant "|" from end of string
            self.audio_manager.socket_send_queue.put(("CALLS-LIST" + calls_data[:-1]).encode("UTF-8"))

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
