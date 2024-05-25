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

    def intersection(self, other) -> Point:
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


LEFT = 0
RIGHT = 1
Direction = Union[LEFT, RIGHT]


class LinearObjectMotion:
    direction: Direction
    velocity: float
    line: Line

    def __init__(self, direction: Direction, velocity: float, line: Line):
        self.direction = direction
        self.velocity = velocity
        self.line = line

    def __str__(self) -> str:
        direction = "LEFT" if self.direction == LEFT else "RIGHT"
        return f"LinearObjectMotion({direction}, {(self.velocity * 3.6):.2f} km/h, {self.line.__str__()})"

    def position_at(self, start: Point, t: float) -> Point:
        distance = self.velocity * t
        if self.direction == LEFT:
            distance = -distance
        distance_x = distance * math.cos(math.atan(self.line.a))
        distance_y = distance * math.sin(math.atan(self.line.a))
        return Point(start.x + distance_x, start.y + distance_y)


class Sample(namedtuple("Sample", ["timestamp", "position"])):
    timestamp: float
    position: Point


class Sensor:
    field_of_view: float  # in degrees
    phi: float  # in radians
    delta: float
    L: float  # distance to path
    d: float  # path width
    n_zones: int
    zone_indices: np.ndarray
    zone_angles: np.ndarray  # angles between zone center and x-axis
    FPS: int

    def __init__(
        self,
        field_of_view: float,
        distance_to_path: float,
        path_width: float,
        FPS: int = 10,
        max_distance: float = 5,
        n_zones: int = 8,
        SNR: float = 10,
    ) -> None:
        # Angles
        self.field_of_view = field_of_view
        self.phi = math.radians(field_of_view)
        self.delta = (math.radians(180) - self.phi) / 2

        # Distances
        self.max_distance = max_distance
        self.L = distance_to_path
        self.d = path_width

        # Lines
        self.left_fov_limit = Line(math.tan(self.delta + self.phi), 0)
        self.right_fov_limit = Line(math.tan(self.delta), 0)

        # Points of intersection between FOV limits and bike path
        self.lt_intersect = self.left_fov_limit.intersection(Line(0, self.L + self.d))
        self.lb_intersect = self.left_fov_limit.intersection(Line(0, self.L))
        self.rt_intersect = self.right_fov_limit.intersection(Line(0, self.L + self.d))
        self.rb_intersect = self.right_fov_limit.intersection(Line(0, self.L))

        # Zones
        self.n_zones = n_zones
        self.zone_indices = np.arange(self.n_zones)
        self.zone_angles = np.array(
            [self._zone_delta_angle(i) for i in self.zone_indices]
        )

        # Sensor config
        self.FPS = FPS
        self.SNR = SNR

    # ---------------------------------- PRIVATE --------------------------------- #

    def _zone_delta_angle(self, zone_idx: int) -> float:
        "Returns the angle between the zone's center and the x-axis."
        return (math.radians(180) - self.delta) - (zone_idx + 0.5) * (
            self.phi / self.n_zones
        )

    def _point_zone_idx(self, point: Point) -> int:
        """Returns index of the zone, in which the point is visible."""
        if point.x == 0:
            return self.n_zones // 2
        angle = math.atan(point.y / point.x)
        if point.x < 0:
            angle += math.radians(180)
        zone_idx = self.n_zones - (angle - self.delta) // (self.phi / self.n_zones) - 1
        if zone_idx < 0 or zone_idx > self.n_zones - 1:
            raise ValueError(f"Point {point} is not in the sensor's field of view.")
        return zone_idx

    def _point_approx(self, zone_idx: int, distance: float) -> Point:
        """Moves the point to the zone's center and returns the new point.
        Sensor will only see the distance to the object in the zone,
        so the best approximation is the distance to the zone's center."""
        delta = self._zone_delta_angle(zone_idx)
        x = distance * math.cos(delta)
        y = distance * math.sin(delta)
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
        if motion.direction == LEFT:
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
        self.plot_zone_boundaries()
        self.plot_zone_center_lines()

    def plot_bike_path(self, **kwargs):
        """Plots the bike path as a blue dashed line."""
        bottom_boundry = Line(0, self.L)
        top_boundry = Line(0, self.L + self.d)
        bottom_boundry.plot(
            linestyle="--", label="Bike path", color="dimgrey", **kwargs
        )
        top_boundry.plot(linestyle="--", color="dimgrey", **kwargs)

    def plot_fov(self, **kwargs):
        """Plots the sensor's field of view as red solid lines."""
        r = self.max_distance
        delta = self.delta
        phi = self.phi
        x = r * math.cos(delta)
        y = r * math.sin(delta)
        plt.plot(
            [0, x],
            [0, y],
            color="red",
            linestyle="-",
            label=f"Field of view {self.field_of_view}°",
            **kwargs,
        )
        x = r * math.cos(delta + phi)
        y = r * math.sin(delta + phi)
        plt.plot([0, x], [0, y], color="red", linestyle="-", **kwargs)

    def plot_zone_center_lines(self):
        """Plots the zone center lines as grey dashed lines."""
        r = self.max_distance
        for i in range(self.n_zones):
            label = "zone center lines" if i == 0 else ""
            delta = self._zone_delta_angle(i)
            x = r * math.cos(delta)
            y = r * math.sin(delta)
            plt.plot([0, x], [0, y], color="grey", linestyle="--", label=label)

    def plot_zone_boundaries(self):
        """Plots the zone boundaries as grey dashed lines."""
        r = self.max_distance
        for i in range(self.n_zones):
            label = "zone boundaries" if i == 0 else ""
            delta = self._zone_delta_angle(i) - self.phi / self.n_zones / 2
            x = r * math.cos(delta)
            y = r * math.sin(delta)
            plt.plot([0, x], [0, y], color="red", linestyle="--", label=label)


def kmh_to_ms(kmh: float) -> float:
    return kmh / 3.6


def main():
    L = 2
    d = 1
    sensor = Sensor(
        field_of_view=36,
        distance_to_path=L,
        path_width=d,
        FPS=30,
        SNR=100,
        n_zones=4,
        max_distance=3.5,
    )

    speed_min = 30
    speed_max = 30
    speeds = np.random.uniform(kmh_to_ms(speed_min), kmh_to_ms(speed_max), 10000)
    speed_estimates = []

    for speed in speeds:
        # Select middle straight path
        # random_y_offset = random.random() * d
        random_y_offset = 0
        p1 = Point(sensor.lb_intersect.x, sensor.lb_intersect.y + random_y_offset)
        p2 = Point(sensor.rb_intersect.x, sensor.rb_intersect.y + random_y_offset)
        trajectory = Line.from_points(p1, p2)
        motion = LinearObjectMotion(LEFT, speed, trajectory)

        samples = sensor.sample_motion(motion)
        timestamps = [sample.timestamp for sample in samples]
        positions = [sample.position for sample in samples]

        x = [x for x, _ in positions]
        y = [y for _, y in positions]
        coefficients = np.polyfit(x, y, 1)
        slope = coefficients[0]
        intercept = coefficients[1]

        # Generate points along the fitted line for plotting
        x_fit = np.linspace(-3, 3, 100)
        y_fit = slope * x_fit + intercept

        plt.plot(x_fit, y_fit)
        trajectory.plot()
        sensor.plot_all()
        plt.scatter(x, y)
        plt.show()

        # Calculate speed estimation error
        s_estimated = positions[-1].distance_to(positions[0])
        t_estimated = timestamps[-1] - timestamps[0]
        speed_estimates.append(s_estimated / t_estimated)

    MSE = sum((speeds - speed_estimates) ** 2) / len(speeds)
    print(
        f"Mean regression error for speeds from {round(kmh_to_ms(speed_min), 2):.2f} m/s to {round(kmh_to_ms(speed_max), 2)} m/s: {round(MSE, 2):.2f} m/s"
    )


if __name__ == "__main__":
    main()
