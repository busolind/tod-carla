import threading

from src.actor.TeleCarlaActor import TeleCarlaActor
from src.carla_bridge.TeleWorld import TeleWorld
from src.utils.utils import synchronized


class TeleOperator(TeleCarlaActor):
    lock = threading.RLock()

    def __init__(self, host, port, tele_world: TeleWorld, controller):
        super().__init__(host, port, tele_world)
        self._last_snapshot = None
        self._controller = controller

    @synchronized(lock)
    def tick(self):
        if self._last_snapshot is not None:
            command = self._controller.do_action()
            self._last_snapshot = None
            ...  # do stuffs

    @synchronized(lock)
    def receive_state_info(self, snapshot):
        self._last_snapshot = snapshot

    def start(self):
        ...
