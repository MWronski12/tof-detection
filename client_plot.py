from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation

import numpy as np
import pandas as pd

from collections import deque

import queue
import threading
import socket
import struct

HOST = "192.168.1.57"
PORT = 8080
INTERVAL = 100
MESSAGE_SIZE = 8 + 4 + 4 * 18 + 4 * 18 + 4
DATA_PROVIDER_BUFFER_LEN = 1024
PLOT_BUFFER_LEN = 128


class DataProvider:
    def __init__(self, default_strategy="confidence"):
        self._strategies = {
            "max": lambda zone_data: max(zone_data[1], zone_data[3]),
            "min": lambda zone_data: min(zone_data[1], zone_data[3]),
            "confidence": lambda zone_data: (zone_data[1] if zone_data[0] >= zone_data[2] else zone_data[3]),
            "target_0": lambda zone_data: zone_data[1],
            "target_1": lambda zone_data: zone_data[3],
        }
        self._strategy = default_strategy

    def get_center_zone_sample(self):
        raise NotImplementedError()

    def get_zone_distances(self):
        raise NotImplementedError()

    def set_strategy(self, strategy):
        self._strategy = strategy

    def _choose_zone_distances(self, measurements):
        zone_distances = []
        for i in range(0, len(measurements), 4):
            zone_data = measurements[i : i + 4]
            zone_distances.append(self._choose_zone_distane(zone_data))

        return zone_distances

    def _choose_zone_distane(self, zone_data):
        return self._strategies[self._strategy](zone_data)


class LiveDataProvider(DataProvider):
    def __init__(self):
        super().__init__()
        self.center_zone_q = queue.Queue()
        self.zone_distances_q = queue.Queue()
        self._worker = threading.Thread(target=self._do_collect_live_data, daemon=True)
        self._worker.start()

    def get_center_zone_sample(self):
        try:
            return self.center_zone_q.get_nowait()
        except queue.Empty:
            return None

    def get_zone_distances(self):
        try:
            return self.zone_distances_q.get_nowait()
        except queue.Empty:
            return None

    def _do_collect_live_data(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))
                print("Successfully connected to data stream!")

                while True:
                    bytes = s.recv(MESSAGE_SIZE)
                    if not bytes:
                        print("Connection closed!")
                        break

                    self._handle_message(bytes)

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

        self.center_zone_q.put((timestamp_ms, distances[4]))
        self.zone_distances_q.put(distances)

    def _choose_zone_distances(self, measurements):
        zone_distances = []
        for i in range(0, len(measurements), 4):
            zone_data = measurements[i : i + 4]
            zone_distances.append(self._choose_zone_distane(zone_data))

        return zone_distances

    def _choose_zone_distane(self, zone_data):
        return self._strategies[self._strategy](zone_data)


class CSVDataProvider(DataProvider):
    def __init__(self, filename="out/test.csv"):
        super().__init__()
        self._data = self._load_data()

    def get_center_zone_sample(self):
        raise NotImplementedError()

    def get_zone_distances(self):
        raise NotImplementedError()

    def _load_data(self, filename="out/test.csv"):
        df = pd.read_csv(filename, header=None)
        df.rename(columns={0: "timestamp", 1: "ambient"}, inplace=True)
        df["measurements"] = df[df.columns[2:]].values.tolist()
        df = df[["timestamp", "ambient", "measurements"]]
        return df


def do_plot_depth_map(data_provider, fig, ax):
    # Create a placeholder image
    zone_distances = np.zeros((3, 3))

    im = ax.imshow(
        zone_distances,
        cmap="autumn",
        extent=[0, 3, 3, 0],
        vmin=0,
        vmax=5000,
    )

    # Create the colorbar outside of the run method
    fig.colorbar(im, ax=ax, orientation="vertical")

    ax.set_title("Depth map")
    ax.set_xticks(np.arange(0, zone_distances.shape[1] + 1, 1))
    ax.set_yticks(np.arange(0, zone_distances.shape[0] + 1, 1))
    ax.grid(True, linestyle="--")

    def run(i):
        zone_distances = data_provider.get_zone_distances()
        if zone_distances is None:
            return

        zone_distances = np.array(zone_distances).reshape(3, 3)

        # Update the data of the image
        im.set_data(zone_distances)

        # Clear the previous text
        for text in ax.texts:
            text.remove()

        # Add new text
        for i in range(zone_distances.shape[0]):
            for j in range(zone_distances.shape[1]):
                ax.text(j + 0.5, i + 0.5, zone_distances[i, j], ha="center", va="center")

    return FuncAnimation(fig, run, interval=INTERVAL, save_count=1024)


def do_plot_center_zones(data_provider, fig, ax, time_span_s=5, y_span_mm=6000):
    props = dict(boxstyle="round", facecolor="wheat", alpha=0.5)
    plt.rcParams["animation.html"] = "jshtml"

    ax.set_title("Center zone")
    ax.set(xlabel="time [s]", ylabel="distance [mm]")
    ax.set_xlim(0, time_span_s)
    ax.set_ylim(0, y_span_mm)
    ax.grid(True)
    scatter = ax.scatter([0], [0], color="orange", s=20)

    distance_box = ax.text(
        0.5,
        0.96,
        str(0),
        transform=ax.transAxes,
        fontsize=36,
        horizontalalignment="center",
        verticalalignment="top",
        bbox=props,
    )

    buffer = deque(maxlen=PLOT_BUFFER_LEN)

    def run(i):
        sample = data_provider.get_center_zone_sample()
        if sample is None:
            return

        timestamp_ms = sample[0]
        dist_mm = sample[1]
        buffer.append((timestamp_ms, dist_mm))

        samples = np.array(buffer, dtype=np.float64)
        samples[:, 0] = samples[:, 0] - samples[0, 0]
        samples[:, 0] /= 1000.0

        t_now = samples[-1, 0]
        left = max(0, t_now - time_span_s / 2)
        right = max(time_span_s, t_now + time_span_s / 2)
        ax.set_xlim(left, right)

        scatter.set_offsets(samples)
        distance_box.set_text(f"{dist_mm:4d} mm")

    return FuncAnimation(fig, run, interval=INTERVAL, save_count=1024)


def main():
    data_provider = LiveDataProvider()
    fig, (ax_depth_map, ax_center_zone) = plt.subplots(1, 2)
    depth_map_ani = do_plot_depth_map(data_provider, fig, ax_depth_map)
    center_zone_ani = do_plot_center_zones(data_provider, fig, ax_center_zone)
    plt.show(block=True)


if __name__ == "__main__":
    main()
