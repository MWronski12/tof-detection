# from notifiable import Notifiable
# from collections import deque
# import threading


# class Buffer(Notifiable):
#     def __init__(self, size=int(10e6)):
#         self._lock = threading.Lock()
#         self._buffer = deque(maxlen=size)

#     def notify(self, message):
#         with self._lock:
#             self._buffer.append(message)

#     def update_all(self, messages):
#         with self._lock:
#             self._buffer.extend(messages)

#     def get_all(self):
#         with self._lock:
#             return list(self._buffer)


# if __name__ == "__main__":
#     buffer = Buffer()
#     buffer.notify("Hello")
#     buffer.notify("World")
#     buffer.update_all(["Foo", "Bar"])
#     print(buffer.get_all())
