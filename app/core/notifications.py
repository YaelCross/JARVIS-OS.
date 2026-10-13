import queue
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Notification:
    source: str
    text: str
    created_at: datetime


class NotificationCenter:
    """Cola donde los vigilantes (Trello, menciones) dejan avisos
    para que JARVIS los diga en cuanto quede libre."""

    def __init__(self):
        self.queue = queue.Queue()

    def notify(self, source, text):
        self.queue.put(Notification(source, text, datetime.now()))

    def drain(self):
        pending = []

        while True:
            try:
                pending.append(self.queue.get_nowait())
            except queue.Empty:
                return pending


notifications = NotificationCenter()
