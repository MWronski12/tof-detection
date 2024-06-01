from mediator import Mediator
from event import Event

from abc import ABC


class Component(ABC):
    def __init__(self, mediator: Mediator):
        self._mediator: Mediator = mediator

    def dispatch(self, event: Event) -> None:
        self._mediator.handle_event(event)
