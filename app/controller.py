from buffer import Buffer
from gui import GUI
from mediator import Mediator
from collector import Collector
from overrides import overrides
from strategy import ZoneDistaceStrategy, TargetZeroStrategy, ConfidenceStrategy
from config import NUM_ZONES


class Controller(Mediator):
    def __init__(self, collector: Collector, strategy: ZoneDistaceStrategy = ConfidenceStrategy()) -> None:
        self._collector = collector
        self._strategy = strategy

        self._buffer = Buffer(span=160)
        self._gui = GUI(mediator=self)

        self._is_playing: bool = False

    def start(self) -> None:
        self._collector.subscribe(self._handle_collector_data)
        self._start_live_data()
        self._gui.start()

    def _handle_collector_data(self, sample: Collector.DataSample) -> None:
        self._buffer.append(sample)

        if self._is_playing:
            data = self._strategy.transform(sample.reshape(1, -1))
            timestamp = data[0][0]
            distance_data = data[0][2:]
            center_zone_distance = distance_data[NUM_ZONES // 2]
            # self._detector.update(timestamp, center_zone_distance)

    def _update_data(self) -> None:
        data = self._buffer.get_data()
        data = self._strategy.transform(data)
        self._gui.update_data(data)
        # self._detector.update_data(data)

    def _stop_live_data(self) -> None:
        self._is_playing = False
        self._collector.stop()

    def _start_live_data(self) -> None:
        self._is_playing = True
        self._collector.start()

    # ----------------------------- Mediator handlers ---------------------------- #

    @overrides
    def handle_rewind(self) -> None:
        self._stop_live_data()
        self._buffer.rewind()
        self._update_data()

    @overrides
    def handle_fast_forward(self) -> None:
        self._stop_live_data()
        self._buffer.fast_forward()
        self._update_data()

    @overrides
    def handle_seek(self, value: int) -> None:
        self._stop_live_data()
        self._buffer.seek(value)
        self._update_data()

    @overrides
    def handle_reset(self) -> None:
        self._buffer.reset()
        self._update_data()
        self._start_live_data()

    @overrides
    def handle_gui_update(self, n_seconds: int) -> None:
        self._update_data()

    @overrides
    def handle_rewind_to_next_motion(self, direction: int = 1) -> None:
        if self._is_playing:
            print("Cannot rewind to next motion while playing")
            return

        self._buffer.skip_to_next_motion(direction)
        self._update_data()
