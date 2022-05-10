import socket
from abc import ABC
from typing import List

from src.network.NetworkChannel import NetworkChannel
from src.utils.decorators import needs_member


class NetworkNode(ABC):

    def __init__(self, host, port):
        self.host = host
        self.port = port
        # self._network_delay_manager = NetworkChannel()
        self._channels: List[NetworkChannel] = []
        self._tele_context = None

    def add_channel(self, channel):
        channel.bind(self)
        self._channels.append(channel)

    def set_context(self, tele_context):
        self._tele_context = tele_context

    def send_message(self, network_message):
        for channel in self._channels:
            channel.send(network_message)

    def quit(self):
        for channel in self._channels:
            channel.quit()

    def run(self, tele_world):
        ...

    @needs_member('_tele_context')
    def start(self, tele_world):
        for channel in self._channels:
            channel.start(self._tele_context)
        self.run(tele_world)