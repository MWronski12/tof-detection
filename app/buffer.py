import threading

import numpy as np

from config import COLUMNS, CENTER_ZONE_IDX


class Buffer:
    def __init__(self, span, size: int = 10**6) -> None:
        self._span = span

        self._lock = threading.Lock()
        self._observed_index = -1  # Index for observed data samples, -1 if live
        self._data_index = -1  # Unbounded index for data samples
        self._buffer_size = size
        self._buffer = self._create_internal_buffer(size)

    def append(self, sample: np.ndarray) -> None:
        with self._lock:
            self._data_index += 1
            self._buffer[self._data_index % self._buffer_size] = sample

    def seek(self, value: int) -> None:
        if self._empty():
            return

        with self._lock:
            data_length = self._get_data_length()
            start_index = self._get_data_start_index()
            offset = int(value / 100.0 * data_length)
            self._observed_index = (start_index + offset) % self._buffer_size

    def rewind(self) -> None:
        with self._lock:
            self._observed_index = (
                self._data_index % self._buffer_size - 1
                if self._is_running_live()
                else (self._observed_index - 1) % self._buffer_size
            )

    def fast_forward(self) -> None:
        with self._lock:
            self._observed_index = -1 if self._is_running_live() else (self._observed_index + 1) % self._buffer_size

    def reset(self) -> None:
        with self._lock:
            self._observed_index = -1

    def skip_to_next_motion(self, direction: int = 1) -> None:
        with self._lock:
            if self._empty() or self._is_running_live():
                return

            index = self._observed_index
            index = self._get_current_motion_end_index(index, direction)
            index = self._get_next_motion_start_index(index, direction)
            if direction == 1:
                index = self._get_current_motion_end_index(index, direction)

            self._observed_index = index

    def get_data(self) -> np.ndarray:
        with self._lock:
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
        return self._observed_index == -1

    def _empty(self) -> bool:
        return self._data_index == -1

    def _get_data_slice(self, start_index: int, end_index: int) -> np.ndarray:
        if start_index < end_index:
            return self._buffer[start_index:end_index]
        else:
            return np.concatenate((self._buffer[start_index:], self._buffer[:end_index]))

    def _get_data_length(self) -> int:
        return min(self._buffer_size, self._data_index + 1)

    def _get_data_start_index(self) -> int:
        return max(0, self._data_index - self._buffer_size)

    def _get_current_motion_end_index(self, index: int, direction: int = 1) -> int:
        end_index = self._data_index % self._buffer_size

        while index != end_index and self._motion_is_present_in_center_zone(index):
            index = (index + direction) % self._buffer_size

        return index

    def _get_next_motion_start_index(self, index: int, direction: int = 1) -> int:
        end_index = self._data_index % self._buffer_size

        while index != end_index and not self._motion_is_present_in_center_zone(index):
            index = (index + direction) % self._buffer_size

        return index

    def _motion_is_present_in_center_zone(self, index: int) -> bool:
        if index < 0 or index >= self._buffer_size or index > self._data_index:
            raise ValueError("Invalid index")

        _, dist0, _, dist1 = self._buffer[index][2:].reshape(-1, 4)[CENTER_ZONE_IDX]

        return dist0 != -1 or dist1 != -1
