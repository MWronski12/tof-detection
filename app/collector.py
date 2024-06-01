import threading


class Collector:
    def __init__(self):
        self._event = threading.Event()
        self._worker = None
        self._observers = []

    def subscribe(self, observer):
        self._observers.append(observer)

    def unsubscribe(self, observer):
        self._observers.remove(observer)

    def start(self):
        if self._worker is None or not self._worker.is_alive():
            self._worker = threading.Thread(target=self._run, daemon=True)
            self._worker.start()

        self._event.set()

    def stop(self):
        self._event.clear()

    def _dispatch(self, data):
        for observer in self._observers:
            observer(data)

    def _run(self):
        raise NotImplementedError("Subclasses must implement _run method")
