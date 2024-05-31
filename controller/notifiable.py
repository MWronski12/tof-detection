class Notifiable:
    def notify(self, message):
        raise NotImplementedError("notify method must be implemented in subclass")

    def update_all(self, messages):
        raise NotImplementedError("update_all method must be implemented in subclass")
