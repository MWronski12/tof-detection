from observable import Observable
import time


class CSVCollector(Observable):
    def __init__(self, file_path):
        super().__init__()
        self._file_path = file_path
        self._last_timestamp = None

    def start(self):
        with open(self._file_path, "r") as f:
            print("Successfully opened csv file:", self._file_path)

            for line in f:
                self._handle_message(line)

            print("Finished reading csv file")

    def _handle_message(self, line):
        data = line.strip().split(",")
        data = list(map(int, data))

        current_timestamp = data[0]
        if self._last_timestamp is not None:
            time.sleep((current_timestamp - self._last_timestamp) / 1000.0)

        self._last_timestamp = current_timestamp
        self._dispatch(data)


if __name__ == "__main__":
    file_path = "out/data-1717158663.csv"
    collector = CSVCollector(file_path)
    collector.subscribe(lambda data: print(data))
    collector.start()
