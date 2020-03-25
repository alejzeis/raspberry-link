import dbus
import dbus.mainloop.glib


class HandsfreeManager:
	bus = dbus.SystemBus()
	manager = dbus.Interface(bus.get_object('org.ofono', '/'),
							 'org.ofono.Manager')
	# TODO: Support for multiple active calls?
	current_call = ""

	bt_mgr = None

	def __init__(self, bt_mgr):
		self.bt_mgr = bt_mgr

		modems = self.manager.GetModems()
		modem = modems[0][0]

		print("Using modem %s" % modem)

		vcmanager = dbus.Interface(self.bus.get_object('org.ofono', modem), 'org.ofono.VoiceCallManager')

		vcmanager.connect_to_signal("CallAdded", self._call_added)

		vcmanager.connect_to_signal("CallRemoved", self._call_removed)

	def answer_call(self, path):
		call = dbus.Interface(self.bus.get_object('org.ofono', path), 'org.ofono.VoiceCall')
		if call:
			call.Answer()
			print("    Voice Call [ %s ] Answered" % (path))
			self.current_call = path
			return True
		else:
			return False

	def hangup_call(self, path):
		if self.current_call != path:
			raise RuntimeError("Current call is different than call to hangup!")

		call = dbus.Interface(self.bus.get_object('org.ofono', path), 'org.ofono.VoiceCall')
		if call:
			call.Hangup()
			self.current_call = ""
			return True
		else:
			return False

	def _call_added(self, path):
		print("Call Added: " + path)

	def _call_removed(self, path):
		print("Call Removed: " + path)
