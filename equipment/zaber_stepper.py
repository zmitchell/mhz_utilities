import struct
from enum import Enum
from serial import Serial
from logzero import logger


class StepperCmd(Enum):
    MOVE = 20
    INIT = 52
    GETPOS = 60


class Stepper:
    def __init__(self, port):
        self.ser = Serial(port, 9600, 8, 'N', 1, timeout=5)
        logger.info(f"[STEP] opened {port} for stepper")
        self.device = 1

    def _send(self, cmd, data):
        packet = struct.pack("<BBl", self.device, cmd, data)
        logger.debug(f"[STEP] sending packet: {packet}")
        self.ser.write(packet)

    def _recv(self):
        response = self.ser.read(6)
        logger.debug(f"[STEP] received response: {response}")
        return response

    def move(self, target_pos):
        logger.debug(f"[STEP] moving to {target_pos}")
        self._send(StepperCmd.MOVE.value, target_pos)
        logger.debug(f"[STEP] waiting until the destination is reached")
        curr_pos = 0
        while curr_pos != target_pos:
            curr_pos = self.pos()
            logger.debug(f"[STEP] still moving ({curr_pos} / {target_pos})")
        logger.debug("[STEP] done moving")

    def pos(self):
        logger.debug("[STEP] getting current position")
        self._send(StepperCmd.GETPOS.value, 0)
        resp = self._recv()
        logger.debug(f"[STEP] received response: {resp}")
        value = 256**3 * resp[5] + 256**2 * resp[4] + 256 * resp[3] + resp[2]
        logger.debug(f"[STEP] translates to: {value}")
        if resp[5] > 127:
            value = -256**4
            logger.debug(f"[STEP] setting value to {value}")
        return value
