from enum import Enum
from dataclasses import dataclass


class EventType(Enum):
    MEASUREMENT = 1  # List of values representing a measurement, like stored in CSV
    DISTANCE_DATA = 2  # tuple of timestamp and list of distancess

    REWIND = 3
    FAST_FORWARD = 4
    SEEK = 5
    RESET = 6


@dataclass
class Event:
    type: EventType
    data: any = None
