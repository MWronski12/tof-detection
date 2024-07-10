from component import Component
from mediator import Mediator
from motion import Motion
from config import NUM_ZONES

from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider
from matplotlib.gridspec import GridSpec
from matplotlib.artist import Artist

from typing import Optional
from abc import ABC, abstractmethod
from datetime import datetime
from overrides import overrides

import numpy as np
import threading


class Animator(ABC):
    def __init__(self, fig, ax):
        self._fig = fig
        self._ax = ax

    @abstractmethod
    def update(self, data: np.ndarray, motion: Optional[Motion]) -> list[Artist]:
        pass


class DepthMapAnimator(Animator):
    def __init__(self, fig, ax):
        super().__init__(fig, ax)

        zone_distances = np.zeros((3, 3))

        self._im = self._ax.imshow(
            zone_distances,
            cmap="autumn",
            extent=[0, 3, 3, 0],
            vmin=0,
            vmax=5000,
        )

        self._ax.set_title("Depth map")
        self._fig.colorbar(self._im, ax=self._ax, orientation="vertical")
        self._ax.set_xticks(np.arange(0, zone_distances.shape[1] + 1, 1))
        self._ax.set_yticks(np.arange(0, zone_distances.shape[0] + 1, 1))
        self._ax.grid(True, linestyle="--")

    @overrides
    def update(self, data: np.ndarray, motion: Optional[Motion]) -> list[Artist]:
        if len(data) == 0:
            return []

        zone_distances = data[-1][2:]
        zone_distances = zone_distances.reshape(3, 3)
        zone_distances[zone_distances == -1] = 5000

        self._im.set_data(zone_distances)

        for text in self._ax.texts:
            text.remove()

        for i in range(zone_distances.shape[0]):
            for j in range(zone_distances.shape[1]):
                self._ax.text(j + 0.5, i + 0.5, zone_distances[i, j], ha="center", va="center")

        return [self._im]


class CenterZoneAnimator(Animator):
    def __init__(self, fig, ax, time_span_s=5, y_span_mm=6000):
        super().__init__(fig, ax)

        self._time_span_s = time_span_s
        self._y_span_mm = y_span_mm

        self._ax.set_title("Center zone")
        self._ax.set(xlabel="time [s]", ylabel="distance [mm]")
        self._ax.set_xlim(0, self._time_span_s)
        self._ax.set_ylim(0, self._y_span_mm)
        self._ax.grid(True)

        self._scatter = self._ax.scatter([0], [0], color="orange", s=20)

    @overrides
    def update(self, data: np.ndarray, motion: Optional[Motion]) -> list[Artist]:
        if len(data) < 2:
            return []

        if motion != None:
            self.update_motion(motion)
        else:
            for line in self._ax.get_lines():
                line.remove()

        center_zone_data = data[:, [0, 2 + NUM_ZONES // 2]]  # timestamp, center_zone_distance

        t_now = center_zone_data[-1][0]
        left = t_now - self._time_span_s * 3 / 4 * 1000
        right = t_now + self._time_span_s * 1 / 4 * 1000
        self._ax.set_xlim(left, right)

        self._scatter.set_offsets(center_zone_data)

        return [self._scatter]

    def update_motion(self, motion: Motion) -> None:
        for s in motion._monotonic_series:
            color = "red" if s.dist_end < s.dist_start else "blue"
            self._ax.plot(
                [sample[0] for sample in s._samples],
                [sample[1] for sample in s._samples],
                color=color,
            )


class WidgetAnimator(Animator):
    def __init__(self, fig, ax):
        super().__init__(fig, ax)

        self._ax.axis("off")

        args = {
            "fontsize": 22,
            "transform": self._ax.transAxes,
            "bbox": {"facecolor": "orange", "alpha": 0.5},
            "verticalalignment": "bottom",
        }

        self._time = self._ax.text(0, 0.75, "time: -1", **args)
        self._distance = self._ax.text(0, 0.5, "distance: -1", **args)
        self._timestamp = self._ax.text(0, 0.25, "timestamp: -1", **args)
        self._motion_velocity = self._ax.text(0, 0, "velocity: -1", **args)

    @overrides
    def update(self, data: np.ndarray, motion: Optional[Motion]) -> list[Artist]:
        if len(data) == 0:
            return []

        if motion != None:
            self._motion_velocity.set_text(f"velocity: {motion.velocity:.2f} kmh")
        else:
            self._motion_velocity.set_text(f"velocity: -1")

        timestamp = data[-1][0] / 1000.0
        distance = data[-1][2 + NUM_ZONES // 2]
        time = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S.%f")[:-3]

        self._timestamp.set_text(f"timestamp: {int(timestamp * 1000)} ms")
        self._distance.set_text(f"distance: {distance} mm")
        self._time.set_text(f"time: {time}")

        return [self._ax.texts]


class GUI(Component):
    def __init__(self, mediator: Mediator) -> None:
        super().__init__(mediator)

        self._center_zone_time_span_s = 5
        self._refresh_interval_ms = 100

        self._data_lock = threading.Lock()
        self._data = np.array([], dtype=np.int64)

        self._fig = plt.figure()
        gs = GridSpec(3, 5, figure=self._fig)

        self._widgets_ax = self._fig.add_subplot(gs[:1, :3])
        self._center_zone_ax = self._fig.add_subplot(gs[1:, :3])
        self._depth_map_ax = self._fig.add_subplot(gs[:, 3:])

        self._widget_animator = WidgetAnimator(self._fig, self._widgets_ax)
        self._center_zone_animator = CenterZoneAnimator(self._fig, self._center_zone_ax, self._center_zone_time_span_s)
        self._depth_map_animator = DepthMapAnimator(self._fig, self._depth_map_ax)
        self._animators: list[Animator] = [
            self._widget_animator,
            self._center_zone_animator,
            self._depth_map_animator,
        ]

        self._ani = FuncAnimation(self._fig, self._animate, interval=self._refresh_interval_ms, save_count=200)

        self._seek_ax = self._fig.add_axes([0.1, 0.02, 0.8, 0.02])
        self._slider = Slider(
            ax=self._seek_ax,
            label="Time",
            valmin=0,
            valmax=100,
            valinit=100,
            orientation="horizontal",
            dragging=True,
            color="orange",
            track_color="gray",
        )

        self._fig.canvas.mpl_connect("key_press_event", self._on_key_press)
        self._slider.on_changed(self._on_seek_submit)

    def start(self) -> None:
        plt.show()

    def update_data(self, data: np.ndarray, motion: Optional[Motion]) -> None:
        with self._data_lock:
            for animator in self._animators:
                animator.update(data, motion)

    def _animate(self, frame) -> None:
        self.gui_update(self._center_zone_time_span_s)

    def _on_key_press(self, event) -> None:
        if event.key == "a":
            self.rewind()

        elif event.key == "d":
            self.fast_forward()

        elif event.key == "r":
            self._slider.set_val(100)
            self.reset()

        elif event.key == "n":
            self.rewind_to_next_motion(direction=1)

        elif event.key == "b":
            self.rewind_to_next_motion(direction=-1)

        elif event.key == "1":
            self.change_strategy("target_0")

        elif event.key == "2":
            self.change_strategy("confidence")

    def _on_seek_submit(self, value: int) -> None:
        self.seek(value)
