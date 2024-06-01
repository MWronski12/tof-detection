from enum import Enum
from dataclasses import dataclass


class EventType(Enum):
    MEASUREMENT = 1
    DISTANCE_DATA = 2

    REWIND = 3
    FAST_FORWARD = 4
    SEEK = 5
    RESET = 6


@dataclass
class Event:
    type: EventType
    data: any = None
