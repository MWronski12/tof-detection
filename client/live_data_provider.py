import threading
import socket
import struct

import numpy as np

from collections import deque

from data_provider import DataProvider

HOST = "192.168.1.57"
PORT = 8080
MESSAGE_SIZE = 8 + 4 + 4 * 18 + 4 * 18 + 4
DATA_BUFFER_LEN = 256
DIST_MAX = 5000


class LiveDataProvider(DataProvider):
    def __init__(self, host=HOST, port=PORT, buffer_len=DATA_BUFFER_LEN):
        super().__init__()
        self._data_lock = threading.Lock()
        self._timestamps = deque(maxlen=buffer_len)
        self._distances = deque(maxlen=buffer_len)

        self._worker = threading.Thread(target=self._do_collect_live_data, daemon=True)
        self._worker.start()

    def get_center_zone_data(self):
        with self._data_lock:
            if len(self._timestamps) == 0:
                return None

            timestamps = np.array(self._timestamps, dtype=np.float64)
            distances = np.array(self._distances, dtype=np.int16)
            center_zone_data = distances[:, 4].reshape(-1)

            return np.column_stack((timestamps, center_zone_data))

    def get_zone_distances(self):
        with self._data_lock:
            if len(self._timestamps) == 0:
                return None

            zone_distances = np.array(self._distances[-1], dtype=np.int16).reshape(3, 3)
            zone_distances[zone_distances == -1] = DIST_MAX

            return zone_distances

    def _do_collect_live_data(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))
                print("Successfully connected to data stream!")

                while True:
                    try:
                        bytes = s.recv(MESSAGE_SIZE)
                        if not bytes:
                            print("Connection closed!")
                            break

                        self._handle_message(bytes)

                    except Exception as e:
                        print(f"Error: {e}")
                        continue

        except socket.error as e:
            print(f"Socket error: {e}")

    def _handle_message(self, bytes):
        unpacked_data = struct.unpack("<Qi18i18i4x", bytes)
        timestamp_ms = unpacked_data[0]
        ambient_light = unpacked_data[1]
        confidences = unpacked_data[2:20]
        distances = unpacked_data[20:38]

        measurements = [item for pair in zip(confidences, distances) for item in pair]
        distances = self._choose_zone_distances(measurements)

        with self._data_lock:
            self._timestamps.append(timestamp_ms / 1000.0)
            self._distances.append(distances)
