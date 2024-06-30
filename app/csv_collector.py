from collector import Collector

from overrides import overrides
from typing import Optional
import numpy as np
import time


class CSVCollector(Collector):
    def __init__(self, file_path: str, live_mode: bool = False, start_time_ms: int = 0) -> None:
        super().__init__()

        self._file_path = file_path
        self._live_mode = live_mode
        self._start_time_ms = start_time_ms

        self._last_timestamp: Optional[float] = None
        self._last_dispatch_time: Optional[float] = None

    @overrides
    def _start(self) -> None:
        with open(self._file_path, "r") as file:
            print("Successfully opened CSV file")

            for line in file:
                self._event.wait()
                self._handle_message(line)

            print("Reached end of CSV file")

    def _handle_message(self, line: str) -> None:
        data = line.strip().split(",")
        data = np.array(list(map(int, data)), dtype=np.int64)

        timestamp_ms = data[0]
        if self._start_time_ms > timestamp_ms:
            return

        if self._live_mode:
            self._simulate_live_data(timestamp_ms / 1000.0)

        self.dispatch(data)

    def _simulate_live_data(self, timestamp: float) -> None:
        if self._last_timestamp is not None:
            elapsed_time = timestamp - self._last_timestamp
            time_since_last_dispatch = time.time() - self._last_dispatch_time

            if elapsed_time > time_since_last_dispatch:
                time.sleep(elapsed_time - time_since_last_dispatch)
            else:
                print("Warning, data is being processed too slowly")

        self._last_timestamp = timestamp
        self._last_dispatch_time = time.time()
