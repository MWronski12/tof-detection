from buffer import Buffer
from gui import GUI
from detector import Detector
from mediator import Mediator
from motion import Motion
from collector import Collector
from overrides import overrides
from strategy import Strategy, ZoneDistaceStrategy, TargetZeroStrategy, ConfidenceStrategy
from copy import deepcopy


class Controller(Mediator):
    def __init__(self, collector: Collector, strategy: ZoneDistaceStrategy = TargetZeroStrategy()) -> None:
        self._collector = collector
        self._strategy = strategy

        self._buffer = Buffer(span=160)
        self._gui = GUI(mediator=self)
        self._detector = Detector(mediator=self)

        self._is_playing: bool = False

    def start(self) -> None:
        self._collector.subscribe(self._handle_collector_data)
        self._start_live_data()
        self._gui.start()

    def _handle_collector_data(self, sample: Collector.DataSample) -> None:
        self._buffer.append(sample)

        if self._is_playing:
            sample = self._strategy.transform(sample.reshape(1, -1))[0]
            self._detector.append_sample(sample)

    def _update_data(self) -> None:
        data = self._buffer.get_data()
        data = self._strategy.transform(data)
        self._detector.update_data(data)
        motion = self._detector.get_motion()
        self._gui.update_data(data, motion)

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

    @overrides
    def handle_change_strategy(self, strategy: Strategy) -> None:
        self._stop_live_data()

        if strategy == "target_0":
            print("Changing strategy to TargetZeroStrategy")
            self._strategy = TargetZeroStrategy()

        elif strategy == "confidence":
            print("Changing strategy to ConfidenceStrategy")
            self._strategy = ConfidenceStrategy()

        self._update_data()

    @overrides
    def handle_signal_bicycle(self, motion: Motion) -> None:
        # print(f"Bicycle {"approaching" if motion.direction == 1 else "moving away"} {motion.velocity:.2f} kmh detected!")
        pass