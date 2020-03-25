import socket
import threading


class AudioServiceCommunicator:
    sock = None
    recv_thread = None

    active_calls = {}

    def __init__(self, socket_file="/run/raspberrylink_audio.socket"):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(socket_file)
        print("Connected to RaspberryLink Audio socket")

        self.recv_thread = threading.Thread(target=self._process_recv, daemon=True)
        self.recv_thread.start()

    def answer_call(self, path):
        self.sock.send(("CALL-ANSWER~" + path).encode("UTF-8"))

    def hangup_call(self, path):
        self.sock.send(("CALL-HANGUP~" + path).encode("UTF-8"))

    def _process_recv(self):
        print("Listening for data from RaspberryLink Audio process")
        while True:
            data = self.sock.recv(512).decode("UTF-8").split("~")

            if data[0] == "CALL-STATE":
                # Call state change, new incoming call, new outgoing call, or hung up TODO
                pass
            else:
                print("Unknown message from RaspberryLink Audio process " + str(data))