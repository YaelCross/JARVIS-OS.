from enum import Enum


class JarvisState(Enum):

    BOOTING = "BOOTING"
    IDLE = "IDLE"
    LISTENING = "LISTENING"
    PROCESSING = "PROCESSING"
    SPEAKING = "SPEAKING"
    ERROR = "ERROR"