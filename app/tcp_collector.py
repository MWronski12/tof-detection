from collector import Collector
from overrides import overrides

import numpy as np

import socket
import struct


MESSAGE_SIZE = 8 + 4 + 4 * 18 + 4 * 18 + 4


class TCPCollector(Collector):
    def __init__(self, host: str, port: int) -> None:
        super().__init__()

        self._host = host
        self._port = port

    @overrides
    def _start(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self._host, self._port))
            print("Successfully connected to data stream")

            while True:
                self._event.wait()

                try:
                    bytes = self._recv_msg(s, MESSAGE_SIZE)
                    if not bytes:
                        print("Connection closed")
                        break

                    self._handle_message(bytes)

                except Exception as e:
                    print(f"Error: {e}")
                    continue

    def _recv_msg(self, sock: socket, size: int) -> bytes:
        data = b""
        while len(data) < size:
            packet = sock.recv(size - len(data))
            if not packet:
                return None
            data += packet
        return data

    def _handle_message(self, bytes: bytes) -> None:
        unpacked_data = struct.unpack("<Qi18i18i4x", bytes)
        timestamp_ms = unpacked_data[0]
        ambient_light = unpacked_data[1]
        confidences = unpacked_data[2:20]
        distances = unpacked_data[20:38]

        data = [timestamp_ms, ambient_light]
        data += [measurement for pair in zip(confidences, distances) for measurement in pair]
        data = np.array(data, dtype=np.int64)

        self.dispatch(data)
