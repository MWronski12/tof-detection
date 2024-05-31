import numpy as np
from collections import deque
from matplotlib import pyplot as plt
from notifiable import Notifiable


BUFFER_SIZE = 50


class DepthMapAnimator:
    def __init__(self, fig, ax):
        self._fig = fig
        self._ax = ax

        zone_distances = np.zeros((3, 3))

        self._im = self._ax.imshow(
            zone_distances,
            cmap="autumn",
            extent=[0, 3, 3, 0],
            vmin=0,
            vmax=5000,
        )

        self._fig.colorbar(self._im, ax=self._ax, orientation="vertical")
        self._ax.set_title("Depth map")
        self._ax.set_xticks(np.arange(0, zone_distances.shape[1] + 1, 1))
        self._ax.set_yticks(np.arange(0, zone_distances.shape[0] + 1, 1))
        self._ax.grid(True, linestyle="--")

    def update(self, zone_distances):
        zone_distances = np.array(zone_distances).reshape(3, 3)
        zone_distances[zone_distances == -1] = 5000

        self._im.set_data(zone_distances)

        for text in self._ax.texts:
            text.remove()

        for i in range(zone_distances.shape[0]):
            for j in range(zone_distances.shape[1]):
                self._ax.text(j + 0.5, i + 0.5, zone_distances[i, j], ha="center", va="center")


class CenterZoneAnimator:
    def __init__(self, fig, ax, time_span_s=5, y_span_mm=6000):
        self._time_span_s = time_span_s
        self._y_span_mm = y_span_mm

        self._fig = fig
        self._ax = ax

        self._ax.set_title("Center zone")
        self._ax.set(xlabel="time [s]", ylabel="distance [mm]")
        self._ax.set_xlim(0, self._time_span_s)
        self._ax.set_ylim(0, self._y_span_mm)
        self._ax.grid(True)

        self._scatter = self._ax.scatter([0], [0], color="orange", s=20)

        self._distance_box = self._ax.text(
            0.5,
            0.96,
            str(0),
            transform=self._ax.transAxes,
            fontsize=36,
            horizontalalignment="center",
            verticalalignment="top",
            bbox={"boxstyle": "round", "facecolor": "wheat", "alpha": 0.5},
        )

        self._deque = deque(maxlen=BUFFER_SIZE)

    def update(self, timestamp, center_zone):
        self._deque.append((timestamp, center_zone))

        if len(self._deque) < 2:
            return

        data = np.array(self._deque)
        t_now = data[-1][0]
        left = t_now - self._time_span_s / 2
        right = t_now + self._time_span_s / 2
        self._ax.set_xlim(left, right)

        self._scatter.set_offsets(data)
        self._distance_box.set_text(f"{int(data[-1][1])} mm")


class GUI(Notifiable):
    def __init__(self):
        self._fig, (depth_map_ax, center_zone_ax) = plt.subplots(1, 2, figsize=(12, 6))

        self._depth_map = DepthMapAnimator(self._fig, depth_map_ax)
        self._center_zone = CenterZoneAnimator(self._fig, center_zone_ax)

    def start(self):
        plt.show()

    def notify(self, message):
        self._depth_map.update(message.distances)
        self._center_zone.update(message.timestamp, message.distances[4])
        self._fig.canvas.draw()

    # def update_all(self, messages):
    #     self._depth_map.update(messages[-1].distances)
    #     self._center_zone.update(messages[-1].timestamp, messages[-1].distances[4])
    #     self._fig.canvas.draw()
