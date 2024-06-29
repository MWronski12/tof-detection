import threading

import numpy as np

from config import COLUMNS


class Buffer:
    def __init__(self, span, size: int = 10**3) -> None:
        self._span = span

        self._lock = threading.Lock()
        self._observed_index = -1  # Index for observed data samples, -1 if live
        self._data_index = -1  # Unbounded index for data samples
        self._buffer_size = size
        self._buffer = self._create_internal_buffer(size)

    def append(self, data: np.ndarray) -> None:
        with self._lock:
            self._data_index += 1
            self._buffer[self._data_index % self._buffer_size] = data

    def seek(self, value: int) -> None:
        if self._empty():
            return

        with self._lock:
            actual_size = min(self._buffer_size, self._data_index + 1)
            oldest_index = max(0, self._data_index - self._buffer_size)
            offset = int(value / 100.0 * actual_size)
            self._observed_index = (oldest_index + offset) % self._buffer_size

    def rewind(self):
        with self._lock:
            self._observed_index = (
                (self._observed_index - 1) % self._buffer_size
                if self._observed_index != -1
                else self._data_index % self._buffer_size - 1
            )

    def fast_forward(self):
        with self._lock:
            self._observed_index = (self._observed_index + 1) % self._buffer_size if self._observed_index != -1 else -1

    def reset(self):
        with self._lock:
            self._observed_index = -1

    def get_data(self) -> np.ndarray:
        if self._empty():
            return np.array([])

        end_index = self._data_index % self._buffer_size if self._is_running_live() else self._observed_index

        start_index = (
            (end_index - self._span) % self._buffer_size
            if self._data_index >= self._buffer_size
            else max(0, end_index - self._span)
        )

        return self._get_data_slice(start_index, end_index)

    def _create_internal_buffer(self, buffer_size: int) -> np.ndarray:
        return np.zeros((buffer_size, len(COLUMNS)), dtype=np.int64)

    def _is_running_live(self) -> bool:
        with self._lock:
            return self._observed_index == -1

    def _empty(self) -> bool:
        with self._lock:
            return self._data_index == -1

    def _get_data_slice(self, start_index, end_index) -> np.ndarray:
        with self._lock:
            if start_index < end_index:
                return self._buffer[start_index:end_index]
            else:
                return np.concatenate((self._buffer[start_index:], self._buffer[:end_index]))
