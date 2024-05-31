from observable import Observable
import socket
import struct


MESSAGE_SIZE = 8 + 4 + 4 * 18 + 4 * 18 + 4


class TCPCollector(Observable):
    def __init__(self, host, port):
        super().__init__()
        self._host = host
        self._port = port

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self._host, self._port))
            print("Successfully connected to data stream")

            while True:
                bytes = s.recv(MESSAGE_SIZE)
                if not bytes:
                    print("Connection closed")
                    break

                self._handle_message(bytes)

    def _handle_message(self, bytes):
        unpacked_data = struct.unpack("<Qi18i18i4x", bytes)
        timestamp_ms = unpacked_data[0]
        ambient_light = unpacked_data[1]
        confidences = unpacked_data[2:20]
        distances = unpacked_data[20:38]

        data = [timestamp_ms, ambient_light]
        data += [measurement for pair in zip(confidences, distances) for measurement in pair]

        self._dispatch(data)


if __name__ == "__main__":
    host = "192.168.1.57"
    port = 8080
    collector = TCPCollector(host=host, port=port)
    collector.subscribe(lambda data: print(data))
    collector.start()
