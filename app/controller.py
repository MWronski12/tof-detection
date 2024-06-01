from gui import GUI

from message import Message

import threading


class Controller:
    def __init__(self, collector, default_strategy="confidence"):
        self._collector = collector
        self._collector_thread = None

        self._gui = GUI()

        self._strategies = {
            "confidence": lambda zone_data: (zone_data[1] if zone_data[0] >= zone_data[2] else zone_data[3]),
            "target_0": lambda zone_data: zone_data[1],
        }
        self._strategy = default_strategy

    def start(self):
        self._collector.subscribe(self._handle_data)
        self._collector.start()
        self._gui.start()

    def _handle_data(self, data):
        distances = self._choose_zone_distances(data[2:])
        message = Message(data[0] / 1000.0, distances)
        self._gui.notify(message)

    def _choose_zone_distances(self, measurements):
        zone_distances = []
        for i in range(0, len(measurements), 4):
            zone_data = measurements[i : i + 4]
            zone_distances.append(self._choose_zone_distance(zone_data))

        return zone_distances

    def _choose_zone_distance(self, zone_data):
        return self._strategies[self._strategy](zone_data)
