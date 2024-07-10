from component import Component
from mediator import Mediator
from motion import Motion
from monotonic_series import MonotonicSeries
from config import BICYCLE_VELOCITY_THRESHOLD_KMH, CENTER_ZONE_IDX

import numpy as np
import threading

from copy import deepcopy
from typing import Tuple, Optional


class Detector(Component):
    def __init__(
        self, mediator: Mediator, min_samples: int = 2, max_dd: int = 200, max_series_time_delta_ms: int = 200
    ) -> None:
        super().__init__(mediator)

        self._min_samples: int = min_samples
        self._max_dd: int = max_dd
        self._max_series_time_delta_ms: int = max_series_time_delta_ms

        self._samples: list[Tuple[int, int]] = []
        self._prev_direction: int = None
        self._processing_series = False
        self._series: list[MonotonicSeries] = []

        self._motion_lock = threading.Lock()
        self._motion: Optional[Motion] = None

    def append_sample(self, sample: np.ndarray) -> None:
        timestamp_ms, cener_zone_dist_mm = sample[0], sample[2 + CENTER_ZONE_IDX]

        # Make detected motion valid for 3 seconds after detection
        with self._motion_lock:
            if self._motion:
                dt = timestamp_ms - self._motion.time_end
                if dt > 3000 or dt < 0:
                    self._motion = None

        # Flush detected monotonic series into motion
        if (
            not self._processing_series
            and len(self._series) > 0
            and timestamp_ms - self._series[-1].time_end > self._max_series_time_delta_ms
        ):
            self._flush_series()

        self._process_sample((timestamp_ms, cener_zone_dist_mm))

    def update_data(self, data: np.ndarray) -> None:
        self._samples = []
        self._prev_direction = None
        self._processing_series = False
        self._series = []

        for sample in data:
            self.append_sample(sample)

    def get_motion(self) -> Optional[Motion]:
        with self._motion_lock:
            return deepcopy(self._motion)

    def _validate_series_samples(self, samples: list[Tuple[int, int]]) -> bool:
        max_dd_ok = all(abs(samples[i][1] - samples[i - 1][1]) < self._max_dd for i in range(1, len(samples)))
        min_samples_ok = len(samples) >= self._min_samples

        return max_dd_ok and min_samples_ok

    def _process_sample(self, sample: Tuple[int, int]) -> None:
        _, distance_mm = sample

        if distance_mm == -1:
            self._processing_series = False

            if len(self._samples) == 0:
                return

            # End of processed series detected
            if self._validate_series_samples(self._samples):
                series = MonotonicSeries(self._samples)
                self._series.append(series)

            self._samples = []
            self._prev_direction = None

        else:
            self._processing_series = True

            # First sample of a motion
            if len(self._samples) == 0:
                self._samples.append(sample)
                return

            direction = self._samples[-1][1] > distance_mm

            # Second sample of a motion
            if len(self._samples) == 1:
                self._prev_direction = direction

            # Next consecutive sample of a motion
            elif self._prev_direction != direction or abs(self._samples[-1][1] - distance_mm) > self._max_dd:
                if self._validate_series_samples(self._samples):
                    series = MonotonicSeries(self._samples)
                    self._series.append(series)

                self._samples = []
                self._prev_direction = None

            self._samples.append(sample)

    def _flush_series(self):
        with self._motion_lock:
            self._motion = Motion(self._series, self._max_series_time_delta_ms)
            if self._motion.velocity > BICYCLE_VELOCITY_THRESHOLD_KMH:
                self.signal_bicycle(deepcopy(self._motion))

        self._series = []
