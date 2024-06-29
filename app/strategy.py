from abc import ABC, abstractmethod
from overrides import overrides

import numpy as np

from config import NUM_ZONES, NUM_TARGETS, COLUMNS


class ZoneDistaceStrategy(ABC):
    def transform(self, data: np.ndarray) -> np.ndarray:
        if data.shape[0] == 0:
            return data

        if data.shape[1] != len(COLUMNS):
            raise ValueError(f"Expected {len(COLUMNS)} columns, got {data.shape[1]}")

        timestamps = data[:, 0:1]
        ambient_light = data[:, 1:2]
        zone_data = data[:, 2:]
        zone_distances = self._choose_zone_distances(zone_data)

        return np.concatenate([timestamps, ambient_light, zone_distances], axis=1)

    @abstractmethod
    def _choose_zone_distances(self, zone_data: np.ndarray) -> np.ndarray:
        pass


class TargetZeroStrategy(ZoneDistaceStrategy):
    @overrides
    def _choose_zone_distances(self, zone_data: np.ndarray) -> np.ndarray:
        zone_data = zone_data.reshape(-1, 4)  # we have conf0, dist0, conf1, dist1 for each zone
        zone_distances = zone_data[:, 1].reshape(-1, NUM_ZONES)  # we only need dist0
        return zone_distances


class ConfidenceStrategy(ZoneDistaceStrategy):
    @overrides
    def _choose_zone_distances(self, zone_data: np.ndarray) -> np.ndarray:
        zone_distances = []
        for sample in range(len(zone_data)):
            sample_distances = []
            for i in range(NUM_ZONES):
                zone_data_len = NUM_TARGETS * 2  # conf, dist per target
                start = i * zone_data_len
                conf0, dist0, conf1, dist1 = zone_data[sample, start : start + zone_data_len]
                sample_distances.append(dist0 if conf0 >= conf1 else dist1)

            zone_distances.append(sample_distances)

        return zone_distances
