import numpy as np

from typing import Any


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

    def get_center_zone_data(self):
        raise NotImplementedError()

    def get_zone_distances(self):
        raise NotImplementedError()

    def set_strategy(self, strategy):
        self._strategy = strategy

    def _choose_zone_distances(self, measurements):
        zone_distances = []
        for i in range(0, len(measurements), 4):
            zone_data = measurements[i : i + 4]
            zone_distances.append(self._choose_zone_distance(zone_data))

        return zone_distances

    def _choose_zone_distance(self, zone_data):
        return self._strategies[self._strategy](zone_data)
