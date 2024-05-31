class Observable:
    def __init__(self):
        self._observers = []

    def subscribe(self, observer):
        self._observers.append(observer)

    def unsubscribe(self, observer):
        self._observers.remove(observer)

    def _dispatch(self, data):
        for observer in self._observers:
            observer(data)

    def start(self):
        raise NotImplementedError("start method must be implemented in subclass")
