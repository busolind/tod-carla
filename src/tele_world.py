from abc import ABC
from queue import PriorityQueue

from utils import need_member


class TeleWorld(ABC):

    def __init__(self, start_timestamp):
        self._queue = PriorityQueue()
        self._current_timestamp = start_timestamp

    def proceed(self, current_timestamp):
        self._current_timestamp = current_timestamp
        if not self._queue.empty() and self._queue.queue[0].timestamp_scheduled <= self._current_timestamp:
            self._queue.get().event.exec(self)

    def schedule_event_from_now(self, e, time_from_now: int):
        self._queue.put(self.TimingEvent(e, self._current_timestamp + time_from_now))

    def has_events(self) -> bool:
        return not self._queue.empty()

    class TimingEvent:
        def __init__(self, event, timestamp):
            self._event = event
            self._timestamp = timestamp

        @property
        def event(self):
            return self._event

        @property
        def timestamp_scheduled(self) -> int:
            return self._timestamp

        def __lt__(self, e):
            return self._timestamp < e.timestamp
