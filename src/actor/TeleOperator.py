import threading

from src.TeleLogger import TeleLogger
from src.network.NetworkMessage import InstructionNetworkMessage
from src.network.NetworkNode import NetworkNode


class TeleOperator(NetworkNode):
    lock = threading.RLock()

    def __init__(self, host, port, controller):
        super().__init__(host, port)
        self._last_snapshot = None
        self._controller = controller

    def receive_vehicle_state_info(self, tele_vehicle_state):
        self._controller.update_vehicle_state(tele_vehicle_state)
        command = self._controller.do_action()
        self.send_message(InstructionNetworkMessage(command))
        TeleLogger.network_logger.write('I AM tele operator and i received a message')



