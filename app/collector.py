import threading
from component import Component
from mediator import Mediator

from abc import abstractmethod


class Collector(Component):
    def __init__(self, mediator: Mediator):
        super().__init__(mediator)

        self._event = threading.Event()
        self._worker = None

    def start(self):
        if self._worker is None or not self._worker.is_alive():
            self._worker = threading.Thread(target=self._start, daemon=True)
            self._worker.start()

        self._event.set()

    def stop(self):
        self._event.clear()

    @abstractmethod
    def _start(self):
        raise NotImplementedError("Subclasses must implement _run method")
