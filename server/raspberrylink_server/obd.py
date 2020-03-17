import obd


class OBDManager:
    _connection = None

    def connect(self):
        if self._connection is None:
            self._connection = obd.OBD()
        else:
            raise RuntimeError("Attempted to connect OBD when already connected!")

