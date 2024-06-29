from mediator import Mediator

from abc import ABC


class Component(ABC):
    def __init__(self, mediator: Mediator):
        self._mediator: Mediator = mediator

    def rewind(self) -> None:
        self._mediator.handle_rewind()

    def fast_forward(self) -> None:
        self._mediator.handle_fast_forward()

    def seek(self, value: int) -> None:
        """Value is an int between 0 and 100 representing the percentage of the video to seek to."""
        self._mediator.handle_seek(value)

    def reset(self) -> None:
        self._mediator.handle_reset()
