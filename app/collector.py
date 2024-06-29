import threading

from abc import abstractmethod


class Collector:
    def __init__(self):
        self._event = threading.Event()
        self._worker = None
        self._subscribers = []

    def start(self):
        if self._worker is None or not self._worker.is_alive():
            self._worker = threading.Thread(target=self._start, daemon=True)
            self._worker.start()

        self._event.set()

    def stop(self):
        self._event.clear()

    def subscribe(self, callback):
        self._subscribers.append(callback)

    def unsubscribe(self, callback):
        self._subscribers.remove(callback)

    def dispatch(self, data):
        for subscriber in self._subscribers:
            subscriber(data)

    @abstractmethod
    def _start(self):
        raise NotImplementedError("Subclasses must implement _run method")
