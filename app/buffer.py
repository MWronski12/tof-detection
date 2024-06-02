from collections import deque
import threading


class Buffer:
    def __init__(self, span, size=10**6):
        self._span = span

        self._current_index = -1

        self._data_lock = threading.Lock()
        self._data = deque(maxlen=size)

    def append(self, data):
        with self._data_lock:
            self._data.append(data)

    def seek(self, value):
        with self._data_lock:
            self._current_index = int(value / 100.0 * (len(self._data) - 1))

    def rewind(self):
        with self._data_lock:
            if self._current_index == -1:
                self._current_index = len(self._data) - 1

            timestamp = self._data[self._current_index][0]
            while self._current_index > 0 and self._data[self._current_index][0] > timestamp - 200:
                self._current_index -= 1

    def fast_forward(self):
        with self._data_lock:
            if self._current_index == -1:
                self._current_index = len(self._data) - 1

            timestamp = self._data[self._current_index][0]
            while self._current_index < len(self._data) - 1 and self._data[self._current_index][0] < timestamp + 200:
                self._current_index += 1

    def reset(self):
        with self._data_lock:
            self._current_index = -1

    def get_data(self):
        with self._data_lock:
            end = len(self._data) if self._current_index == -1 else self._current_index + 1
            start = max(0, end - self._span)
            return list(self._data)[start:end]
