import numpy as np
import pandas as pd

import threading
import keyboard
import time

from collections import deque

from data_provider import DataProvider

DATA_BUFFER_LEN = 128
DIST_MAX = 5000
INTERVAL = 1000 / 30

# 1. Move the center data to 3/4 of the screen
# 2. Sync center data with depth map



class CSVDataProvider(DataProvider):
    def __init__(self, span=DATA_BUFFER_LEN, file_path="out/test.csv", interval=INTERVAL):
        super().__init__()
        self._df = self._load_data(file_path)
        self._start_stop_event = threading.Event()
        self._current_index_lock = threading.Lock()
        self._current_index = 0
        self._interval = interval
        self._span = span
        self._file_path = file_path

        self._handlers = {
            "space": ("Start/Stop", self._handle_space),
            "left": ("Rewind 1 frame", self._handle_left),
            "right": ("Fast forward 1 frame", self._handle_right),
            # "a": ("Back 5 seconds", self._handle_a),
            # "d": ("Forward 5 seconds", self._handle_d),
            "t": ("Go to <timestamp>", self._handle_t),
            "h": ("Print help", self._print_help),
        }

        self._start_capturing_keyboard()
        self._data_animator = threading.Thread(target=self._do_animate_data, daemon=True)
        self._data_animator.start()

    def get_center_zone_data(self):
        with self._current_index_lock:
            end_index = min(self._current_index + self._span, len(self._df))
            data = self._df.iloc[self._current_index : end_index]

        timestamps = data["timestamp"].apply(lambda t: t / 1000.0)
        center_zone_data = data["measurements"].apply(lambda measurements: measurements[4 * 4 : 5 * 4])
        center_zone_distances = center_zone_data.apply(self._choose_zone_distance)

        return np.vstack([*zip(timestamps.astype(np.float64), center_zone_distances.astype(np.int16))])

    def get_zone_distances(self):
        with self._current_index_lock:
            measurements = self._df.iloc[self._current_index]["measurements"]

        distances = self._choose_zone_distances(measurements)
        return np.array(distances, dtype=np.int16).reshape(3, 3)

    def _load_data(self, file_path):
        df = pd.read_csv(file_path, header=None)
        df.rename(columns={0: "timestamp", 1: "ambient"}, inplace=True)
        df["measurements"] = df[df.columns[2:]].values.tolist()
        df = df[["timestamp", "measurements"]]
        return df

    def _do_animate_data(self):
        while True:
            self._start_stop_event.wait()
            if self._current_index >= len(self._df):
                self._start_stop_event.clear()
                continue

            with self._current_index_lock:
                self._current_index += 1

            time.sleep(self._interval / 1000.0)

    def _start_capturing_keyboard(self):
        def on_press(key):
            if key.name in self._handlers:
                self._handlers[key.name][1]()

        keyboard.on_press(on_press)
        self._print_help()

    def _print_help(self):
        print("========== commands ==========")
        for key, (description, _) in self._handlers.items():
            print(f"- {key}: {description}")
        print("==============================")

    def _handle_space(self):
        if self._start_stop_event.is_set():
            self._start_stop_event.clear()
        else:
            self._start_stop_event.set()

    def _handle_left(self):
        self._start_stop_event.clear()
        with self._current_index_lock:
            self._current_index = max(0, self._current_index - 1)

    def _handle_right(self):
        self._start_stop_event.clear()
        with self._current_index_lock:
            self._current_index = min(len(self._df) - 1, self._current_index + 1)

    def _handle_a(self):
        self._start_stop_event.clear()

    def _handle_d(self):
        self._start_stop_event.clear()
        # with self._current_index_lock:
        #     index = (
        #         self._df["timestamp"]
        #         .apply(lambda t: abs(t - self._df.iloc[self._current_index]["timestamp"] - 5))
        #         .idxmin()
        #     )
        #     self._current_index = index

    def _handle_t(self):
        try:
            timestamp = int(input("Enter timestamp: "))
            with self._current_index_lock:
                index = self._df['timestamp'].searchsorted(timestamp)
                print(index)
                if index < len(self._df):
                    self._current_index = index
                else:
                    print("Timestamp not found!")

        except ValueError:
            print("Invalid timestamp!")
