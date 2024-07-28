"""
Key assumptions and simplifications:

- Object's trajectory is a straight line.
- Object's velocity is constant.
- Only one object is present at a time.
- We assume that all objects are points.

- We operate in a 2D coordinate system.

- Wall is parallel to the bike path.
- Wall is the x-axis.

- Sensor is mounted on the wall at 90 degrees to the wall.
- Sensor is the origin of the coordinate system.

- We approximate the zone distance measurement as a point at the center of that zone with that distance to the sensor.
"""

import math
import random
import numpy as np
from matplotlib import pyplot as plt
from collections import namedtuple
from typing import List, Union, Tuple


class Point:
    x: float
    y: float

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __add__(self, other: "Point") -> "Point":
        return Point(self.x + other.x, self.y + other.y)

    def __mul__(self, by: float) -> "Point":
        return Point(self.x * by, self.y * by)

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def __iter__(self):
        yield self.x
        yield self.y

    def distance_to(self, other) -> float:
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    @staticmethod
    def distance_between(p1, p2) -> float:
        return math.sqrt((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2)


ORIGIN = Point(0, 0)


class Line:
    a: float
    b: float

    def __init__(self, a: float, b: float):
        self.a = a
        self.b = b

    def __call__(self, x: float) -> float:
        return self.a * x + self.b

    def __str__(self) -> str:
        return f"y = {self.a:.2f}x + {self.b:.2f}"

    def intersection(self, other: "Line") -> Point:
        x = (other.b - self.b) / (self.a - other.a)
        y = self.a * x + self.b
        return Point(x, y)

    @classmethod
    def from_points(cls, p1: Point, p2: Point) -> "Line":
        a = (p2.y - p1.y) / (p2.x - p1.x)
        b = p1.y - a * p1.x
        return cls(a, b)

    def plot(self, x_range: Tuple[float, float] = (-3, 3), **kwargs):
        x = np.linspace(*x_range, 100)
        y = self(x)
        plt.plot(x, y, **kwargs)


UP = 0
DOWN = 1
Direction = Union[UP, DOWN]


class LinearObjectMotion:
    direction: Direction
    velocity: float
    line: Line

    def __init__(self, direction: Direction, velocity: float, line: Line):
        self.direction = direction
        self.velocity = velocity
        self.line = line

    def __str__(self) -> str:
        direction = "UP" if self.direction == UP else "DOWN"
        return f"LinearObjectMotion({direction}, {(self.velocity * 3.6):.2f} km/h, {self.line.__str__()})"

    def position_at(self, start: Point, t: float) -> Point:
        distance = self.velocity * t
        if self.direction == UP:
            distance = -distance
        distance_x = distance * math.cos(math.atan(self.line.a))
        distance_y = distance * math.sin(math.atan(self.line.a))
        return Point(start.x + distance_x, start.y + distance_y)


class Sample(namedtuple("Sample", ["timestamp", "position"])):
    timestamp: float
    position: Point


class Sensor:
    def __init__(
        self,
        alpha: float = 0.1645496418780254,  # FOV in radians
        beta: float = 0.9633356408432323,  # Angle between fov and normal to bike path
        L: float = 1,  # distance to path
        d: float = 0.5,  # path width
        FPS: float = 1 / 0.033,
        SNR: float = 10,
        max_range: float = 3.5,
    ) -> None:
        # Angles
        self.alpha = alpha
        self.beta = beta

        # Distances
        self.max_range = max_range
        self.L = L
        self.d = d

        # Lines
        self.left_fov_limit = Line(np.tan(self.alpha + self.beta), 0)
        self.right_fov_limit = Line(np.tan(self.beta), 0)

        # Sensor config
        self.FPS = FPS
        self.SNR = SNR

        # Points of intersection between FOV limits and bike path
        self.lt_intersect = Point(self.L, self.left_fov_limit(self.L))
        self.lb_intersect = Point(self.L, self.right_fov_limit(self.L))
        self.rt_intersect = Point(self.L + self.d, self.left_fov_limit(self.L + self.d))
        self.rb_intersect = Point(
            self.L + self.d, self.right_fov_limit(self.L + self.d)
        )

    # ---------------------------------- PRIVATE --------------------------------- #

    def _point_approx(self, zone_idx: int, distance: float) -> Point:
        """Moves the point to the zone's center and returns the new point.
        Sensor will only see the distance to the object in the zone,
        so the best approximation is the distance to the zone's center."""
        beta = self._zone_beta_angle(zone_idx)
        x = distance * math.cos(beta)
        y = distance * math.sin(beta)
        return Point(x, y)

    def _sampling_timestamps(self, motion: LinearObjectMotion):
        """Returns an array of timestamps, that the sensor would sample the motion at."""
        p1 = Line.intersection(self.left_fov_limit, motion.line)
        p2 = Line.intersection(self.right_fov_limit, motion.line)
        s = p1.distance_to(p2)
        t_start = 0
        t_end = s / motion.velocity
        # Random offset simulates the sensor's sampling frequency
        offset = random.random() / self.FPS
        return np.linspace(
            t_start + offset, t_end, int((t_end - t_start) * self.FPS), endpoint=False
        )

    # ---------------------------------- PUBLIC ---------------------------------- #

    def sample_motion(self, motion: LinearObjectMotion) -> List[Sample]:
        """Simulates sampling of the object's motion by the sensor."""
        if motion.direction == UP:
            p1 = Line.intersection(self.right_fov_limit, motion.line)
        else:
            p1 = Line.intersection(self.left_fov_limit, motion.line)

        timestamps = self._sampling_timestamps(motion)
        positions = [motion.position_at(p1, t) for t in timestamps]
        zone_indices = [self._point_zone_idx(p) for p in positions]
        distances = [p.distance_to(ORIGIN) for p in positions]

        noise_stddev = np.average(distances) / self.SNR
        distances_noisy = [d + random.gauss(0, noise_stddev) for d in distances]

        positions_approx = [
            self._point_approx(i, d) for i, d in zip(zone_indices, distances_noisy)
        ]

        samples = [
            Sample(timestamp=t, position=p)
            for t, p in zip(timestamps, positions_approx)
        ]

        return samples

    # --------------------------------- PLOTTING --------------------------------- #

    def plot_all(self):
        self.plot_bike_path()
        self.plot_fov()
        self.plot_normal_line()
        plt.axis("equal")
        plt.legend()

    def plot_bike_path(self, **kwargs):
        """Plots the bike path as a dimgrey dashed line."""
        plt.axvline(
            x=self.L, linestyle="-", label="Bike path", color="dimgrey", **kwargs
        )
        plt.axvline(
            x=self.L + self.d,
            linestyle="-",
            color="dimgrey",
            **kwargs,
        )
        plt.axvline(
            x=self.L + self.d / 2,
            linestyle="--",
            color="lightblue",
            **kwargs,
        )

    def plot_fov(self, **kwargs):
        """Plots the sensor's field of view as red solid lines."""
        self.left_fov_limit.plot(
            x_range=(0, self.max_range * np.cos(self.alpha + self.beta)),
            linestyle="-",
            color="red",
            label="FOV boundary",
        )
        self.right_fov_limit.plot(
            x_range=(0, self.max_range * np.cos(self.beta)),
            linestyle="-",
            color="red",
        )

    def plot_normal_line(self, **kwargs):
        "Plots line perpendicular to the bike path"
        plt.axhline(y=0, color="black", **kwargs)


def kmh_to_ms(kmh: float) -> float:
    return kmh / 3.6


def main():
    alpha = math.radians(9.428)
    max_dist = 2.25  # L + d
    max_range = 5
    beta = math.radians(60) - alpha / 2
    path_width = 1.5
    dist_to_path = max_dist - path_width

    sensor = Sensor(
        alpha=alpha,
        beta=beta,
        L=dist_to_path,
        d=path_width,
        FPS=1 / 0.033,
        max_range=max_range,
        SNR=10,
    )

    sensor.plot_all()
    plt.show()


if __name__ == "__main__":
    main()
