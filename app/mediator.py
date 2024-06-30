from abc import ABC

class Mediator(ABC):
    def handle_seek(self, value: int) -> None:
        print("Mediator: Seek event not implemented")
        pass

    def handle_rewind(self) -> None:
        print("Mediator: Rewind event not implemented")
        pass

    def handle_fast_forward(self) -> None:
        print("Mediator: Fast forward event not implemented")
        pass

    def handle_reset(self) -> None:
        print("Mediator: Reset event not implemented")
        pass

    def handle_gui_update(self, n_seconds: int) -> None:
        print("Mediator: GUI update event not implemented")
        pass

    def handle_rewind_to_next_motion(self, direction: int = 1) -> None:
        print("Mediator: Rewind to next motion event not implemented")
        pass
