from dataclasses import dataclass


@dataclass
class Message:
    timestamp: float
    distances: list[int]
