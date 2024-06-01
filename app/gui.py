from component import Component
from event import Event, EventType
from mediator import Mediator

from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import TextBox
import numpy as np

from collections import deque
import threading
import copy


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

        return [self._im]


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

        self._text_box = self._ax.text(
            0.5,
            0.96,
            str(0),
            transform=self._ax.transAxes,
            fontsize=22,
            horizontalalignment="center",
            verticalalignment="top",
            bbox={"boxstyle": "round", "facecolor": "wheat", "alpha": 0.5},
        )

    def update(self, center_zone_data):
        if len(center_zone_data) < 2:
            return []

        t_now = center_zone_data[-1][0]
        left = t_now - self._time_span_s * 3 / 4
        right = t_now + self._time_span_s * 1 / 4
        self._ax.set_xlim(left, right)

        self._scatter.set_offsets(center_zone_data)
        self._text_box.set_text(f"{int(t_now * 1000)} ms / {int(center_zone_data[-1][1])} mm")

        return [self._scatter, self._text_box]


class GUI(Component):
    def __init__(self, mediator: Mediator, buffer_size):
        super().__init__(mediator)

        self._data_lock = threading.Lock()
        self._data = deque(maxlen=buffer_size)

        self._fig, (depth_map_ax, center_zone_ax) = plt.subplots(1, 2)
        self._depth_map = DepthMapAnimator(self._fig, depth_map_ax)
        self._center_zone = CenterZoneAnimator(self._fig, center_zone_ax)
        self._ani = FuncAnimation(self._fig, self._animate, interval=100, save_count=1000)

        self._fig.canvas.mpl_connect("key_press_event", self._on_key_press)
        self._text_box_ax = self._fig.add_axes([0.1, 0.01, 0.3, 0.05])
        self._text_box = TextBox(self._text_box_ax, "Seek to timestamp: ")
        self._text_box.on_submit(self._on_text_submit)

    # ------------------------------------ GUI ----------------------------------- #

    def start(self):
        plt.show()

    def _animate(self, frame):
        with self._data_lock:
            if len(self._data) == 0:
                return

            zone_distances = copy.deepcopy(self._data[-1][1])
            center_zone_data = [(timestamp, distances[4]) for timestamp, distances in self._data]

        animators = []
        animators += self._depth_map.update(zone_distances)
        animators += self._center_zone.update(center_zone_data)

        return animators

    # -------------------------- Zone Distances Conusmer ------------------------- #

    def append_data(self, sample):
        with self._data_lock:
            timestamp = sample[0]
            distances = sample[1]
            self._data.append((timestamp, distances))

    def update_data(self, data):
        with self._data_lock:
            self._data.clear()
            self._data.extend(data)

    # --------------------------------- Component -------------------------------- #

    def _on_key_press(self, event):
        if event.key == "left":
            self.dispatch(Event(type=EventType.REWIND, data=None))
        elif event.key == "right":
            self.dispatch(Event(type=EventType.FAST_FORWARD, data=None))
        elif event.key == "r":
            self.dispatch(Event(type=EventType.RESET, data=None))

    def _on_text_submit(self, text):
        try:
            timestamp = int(text)
            self.dispatch(Event(type=EventType.SEEK, data=timestamp))

        except ValueError:
            print("Invalid timestamp format. Please enter a valid integer value as timestamp ms.")
