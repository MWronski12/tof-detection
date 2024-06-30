import threading

from numpy.typing import NDArray
import numpy as np

from abc import abstractmethod
from typing import Optional, Callable


class Collector:
    DataSample = NDArray[np.int64]
    Subscriber = Callable[[DataSample], None]

    def __init__(self) -> None:
        self._event = threading.Event()
        self._worker: Optional[threading.Thread] = None
        self._subscribers: list[Collector.Subscriber] = []

    @abstractmethod
    def _start(self) -> None:
        raise NotImplementedError("Subclasses must implement _run method")

    def start(self) -> None:
        if self._worker is None or not self._worker.is_alive():
            self._worker = threading.Thread(target=self._start, daemon=True)
            self._worker.start()

        self._event.set()

    def stop(self) -> None:
        self._event.clear()

    def subscribe(self, callback: Subscriber) -> None:
        self._subscribers.append(callback)

    def unsubscribe(self, callback: Subscriber) -> None:
        self._subscribers.remove(callback)

    def dispatch(self, sample: DataSample) -> None:
        for subscriber in self._subscribers:
            subscriber(sample)
