from time import sleep
import dbus
import dbus.mainloop.glib
import threading
import logging


class DummyHandsfreeManager:
    def __init__(self):
        pass

    def answer_call(self, path):
        pass

    def hangup_call(self, path):
        pass


class HandsfreeManager:
    bus = None
    manager = None
    modems = None

    bt_mgr = None

    poll_thread = None

    logger = logging.getLogger("RL-HandsfreeManager")

    def __init__(self, bt_mgr):
        self.bt_mgr = bt_mgr

        self.logger.setLevel(logging.INFO)

        self.bus = dbus.SystemBus()
        self.manager = dbus.Interface(self.bus.get_object('org.ofono', '/'), 'org.ofono.Manager')

        self.modems = self.manager.GetModems()

        for modem, props in self.modems:
            self.logger.info("Detected Modem: " + str(modem))

        self.poll_thread = threading.Thread(target=self._poll_for_calls, daemon=True)
        self.poll_thread.start()

    def _poll_for_calls(self):
        self.logger.debug("Now polling for calls.")

        while True:
            self.modems = self.manager.GetModems()  # Update list in case of new modems from newly-paired devices

            for modem, modem_props in self.modems:
                if "org.ofono.VoiceCallManager" not in modem_props["Interfaces"]:
                    continue

                mgr = dbus.Interface(self.bus.get_object('org.ofono', modem), 'org.ofono.VoiceCallManager')

                calls = mgr.GetCalls()

                for path, properties in calls:
                    state = properties['State']
                    name = properties['Name']
                    incoming_line = ""
                    line_ident = properties['LineIdentification']
                    if state == "incoming":
                        incoming_line = properties['IncomingLine']

                    if self.bt_mgr.active_connection is not None:
                        self.bt_mgr.active_connection.send("CALL-STATE~" + modem + "~" + state + "~"
                                                           + name + "~" + line_ident + "~" + incoming_line)

            sleep(1)

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
