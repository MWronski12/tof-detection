from component import Component
from mediator import Mediator
from config import DIST_TO_PATH, CENTER_ZONE_IDX

import numpy as np

from typing import Literal, Optional
from dataclasses import dataclass


Direction = Literal["approaching", "departing"]


@dataclass
class Motion:

    @dataclass
    class Sample:
        timestamp_ms: int
        distance_mm: int

    direction: Direction
    samples: list[Sample]

    def calculate_velocity_kmh(self) -> float:
        if len(self.samples) < 2:
            return -1

        start = self.samples[0]
        end = self.samples[-1]

        dd = end.distance_mm - start.distance_mm
        dt = end.timestamp_ms - start.timestamp_ms

        velocity = (end / np.sqrt(end**2 - DIST_TO_PATH**2)) * (dd / dt) * 3.6

        return velocity if self.direction == "approaching" else -velocity


class Detector(Component):
    def __init__(self, mediator: Mediator) -> None:
        super().__init__(mediator)

        self._samples: list[Motion.Sample] = []
        self._last_motion: Optional[Motion] = None
        self._direction: Optional[Direction] = None

    def update_data(self, data: np.ndarray) -> None:
        self._samples.clear()
        for sample in data:
            self.append(sample)

    def append(self, sample: np.ndarray) -> None:
        sample = Motion.Sample(timestamp_ms=sample[0], distance_mm=sample[2 + CENTER_ZONE_IDX])

        if len(self._samples) == 0:
            self._samples.append(sample)

        elif len(self._samples) == 1:
            self._samples.append(sample)
            sample0 = self._samples[0]
            sample1 = self._samples[1]
            self._direction = self._determine_direction(sample0, sample1)

        else:
            previous_sample = self._samples[-1]
            direction = self._determine_direction(previous_sample, sample)

            if direction == self._direction:
                self._samples.append(sample)

            else:
                motion = Motion(direction=self._direction, samples=self._samples)
                self._evaluate_motion(motion)
                self._direction = None
                self._samples.clear()

    def _evaluate_motion(self, motion: Motion):
        print(motion.calculate_velocity_kmh())

    def _determine_direction(self, first: Motion.Sample, second: Motion.Sample) -> Direction:
        return "approaching" if second.distance_mm > first.distance_mm else "departing"
