from buffer import Buffer
from gui import GUI
from mediator import Mediator
from event import Event, EventType
from collector import Collector


SPAN = 150  # How many data points at once will be fetched from buffer and passed to GUI


class Controller(Mediator):
    def __init__(self, default_strategy="confidence"):
        self._handlers = {
            EventType.MEASUREMENT: self._handle_measurement,
            EventType.REWIND: self._handle_rewind,
            EventType.FAST_FORWARD: self._handle_fast_forward,
            EventType.SEEK: self._handle_seek,
            EventType.RESET: self._handle_reset,
        }

        self._collector = None
        self._is_playing = True

        self._buffer = Buffer(span=SPAN)
        self._gui = GUI(mediator=self, buffer_size=SPAN)

        self._strategies = {
            "confidence": lambda zone_data: (zone_data[1] if zone_data[0] >= zone_data[2] else zone_data[3]),
            "target_0": lambda zone_data: zone_data[1],
            "avg": lambda zone_data: (zone_data[1] + zone_data[3]) / 2,
        }
        self._strategy = default_strategy

    def set_collector(self, collector: Collector):
        self._collector = collector

    def start(self):
        self._collector.start()
        self._gui.start()

    # ------------------------------ Event handlers ------------------------------ #

    def handle_event(self, event: Event) -> None:
        if event.type in self._handlers:
            self._handlers[event.type](event)

    def _handle_measurement(self, event: Event) -> None:
        self._buffer.append(event.data)

        if self._is_playing:
            distances = self._choose_zone_distances(event.data)
            sample = event.data[0] / 1000.0, distances
            self._gui.append_data(sample)

    def _handle_rewind(self, event: Event) -> None:
        self._is_playing = False
        self._buffer.rewind()
        self._update_data()

    def _handle_fast_forward(self, event: Event) -> None:
        self._is_playing = False
        self._buffer.fast_forward()
        self._update_data()

    def _handle_seek(self, event: Event) -> None:
        self._is_playing = False
        self._buffer.seek(event.data)
        self._update_data()

    def _handle_reset(self, event: Event) -> None:
        self._buffer.reset()
        self._update_data()
        self._is_playing = True

    # --------------------------------- Strategy --------------------------------- #

    def _update_data(self):
        measurements = self._buffer.get_data()
        data = []
        for measurement in measurements:
            timestamp = measurement[0] / 1000.0
            zone_distances = self._choose_zone_distances(measurement)
            data.append((timestamp, zone_distances))

        self._gui.update_data(data)
        # self._detector.update_data(data)

    def _choose_zone_distances(self, measurement):
        measurement = measurement[2:]
        zone_distances = []
        for i in range(0, len(measurement), 4):
            zone_data = measurement[i : i + 4]
            zone_distances.append(self._choose_zone_distance(zone_data))

        return zone_distances

    def _choose_zone_distance(self, zone_data):
        return self._strategies[self._strategy](zone_data)
