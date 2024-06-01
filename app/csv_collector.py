from collector import Collector
from mediator import Mediator
from event import Event, EventType

import time


class CSVCollector(Collector):
    def __init__(self, mediator: Mediator, file_path):
        super().__init__(mediator)

        self._file_path = file_path
        self._last_timestamp = None
        self._last_dispatch_time = None

    def _start(self):
        with open(self._file_path, "r") as file:
            print("Successfully opened CSV file")

            for line in file:
                self._event.wait()
                self._handle_message(line)

            print("Reached end of CSV file")

    def _handle_message(self, line):
        data = line.strip().split(",")
        data = list(map(int, data))

        if self._last_timestamp is not None:
            elapsed_time = data[0] / 1000.0 - self._last_timestamp
            time_since_last_dispatch = time.time() - self._last_dispatch_time
            if elapsed_time > time_since_last_dispatch:
                time.sleep(elapsed_time - time_since_last_dispatch)

        self._last_timestamp = data[0] / 1000.0
        self._last_dispatch_time = time.time()

        self.dispatch(event=Event(EventType.MEASUREMENT, data=data))
