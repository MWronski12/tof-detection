from config import DIST_TO_PATH
from typing import Tuple
import numpy as np


class MonotonicSeries:
    def __init__(self, samples: list[Tuple[int, int]]) -> None:
        self._validate_monotonicity(samples)
        self._samples = samples

        self.time_start = samples[0][0]
        self.time_end = samples[-1][0]
        self.time_total = self.time_end - self.time_start

        self.dist_start = samples[0][1]
        self.dist_end = samples[-1][1]
        self.dist_avg = sum(dist for _, dist in samples) / len(samples)

        self.direction = -1 if self.dist_start < self.dist_end else 1
        self.velocity = self._calculate_avg_velocity()

    def __len__(self) -> int:
        return len(self._samples)

    def _validate_monotonicity(self, samples: list[Tuple[int, int]]) -> None:
        assert len(samples) >= 2

        prev_direction = samples[1] > samples[0]
        for i in range(1, len(samples)):
            direction = samples[i] > samples[i - 1]
            assert prev_direction == direction

    def _calculate_avg_velocity(self) -> float:
        velocities = []
        for i in range(1, len(self._samples)):
            t1, d1 = self._samples[i - 1]
            t2, d2 = self._samples[i]

            dt = t2 - t1
            dd = d2 - d1

            if (dt == 0) or (d2**2 - DIST_TO_PATH**2 <= 0):
                print("WARNING: Zero division would occur, skipping sample")
                continue

            velocity = d2 / np.sqrt(d2**2 - DIST_TO_PATH**2) * dd / dt * 3.6
            velocities.append(velocity)

        return abs(sum(velocities) / len(velocities)) if len(velocities) != 0 else 0
