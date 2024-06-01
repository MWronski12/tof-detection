from collector import Collector
import time


class CSVCollector(Collector):
    def __init__(self, file_path):
        super().__init__()
        self._file_path = file_path
        self._last_timestamp = None
        self._last_dispatch_time = None

    def _run(self):
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

        self._dispatch(data)


if __name__ == "__main__":
    file_path = "out/data-1717158663.csv"
    collector = CSVCollector(file_path)
    collector.subscribe(lambda data: print(data))
    collector.start()
