from mediator import Mediator
from strategy import Strategy

from abc import ABC
from typing import Literal


class Component(ABC):
    def __init__(self, mediator: Mediator) -> None:
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

    def gui_update(self, n_seconds: int) -> None:
        self._mediator.handle_gui_update(n_seconds)

    def rewind_to_next_motion(self, direction: int = 1) -> None:
        self._mediator.handle_rewind_to_next_motion(direction)

    def change_strategy(self, strategy: Strategy) -> None:
        self._mediator.handle_change_strategy(strategy)
