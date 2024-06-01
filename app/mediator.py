from abc import ABC, abstractmethod
from event import Event


class Mediator(ABC):
    @abstractmethod
    def handle_event(self, event: Event) -> None:
        pass
