import serial
from serial import Serial
from logzero import logger


class PEM:
    def __init__(self, port):
        params = {
            "baudrate": 2400,
            "bytesize": serial.EIGHTBITS,
            "stopbits": serial.STOPBITS_ONE,
            "timeout": 5,
        }
        self.ser = Serial(port, **params)
        logger.info(f"[PEM] opened {port} for PEM")

    def set_wl(self, wl_str):
        cmd = f"W:{wl_str}\r\n".encode("utf-8")
        logger.debug(f"[PEM] setting wavelength: {cmd}")
        self.ser.reset_input_buffer()
        self.ser.write(cmd)
        resp = self.ser.read(3)
        logger.debug(f"[PEM] received response: {resp}")
        if resp != b"\n\r*":
            logger.error(f"[PEM] received response {resp}, expected '\\n\\r*'")
            raise ValueError(f"sent {cmd}, got {resp}")

    def enable_ret(self):
        cmd = b"I:0\r\n"  # enable retardation
        logger.debug(f"[PEM] enabling retardation: {cmd}")
        self.ser.reset_input_buffer()
        self.ser.write(cmd)
        resp = self.ser.read(3)
        logger.debug(f"[PEM] received response: {cmd}")
        if resp != b"\n\r*":
            logger.error(f"[PEM] received response {resp}, expected '\\n\\r*'")
            raise ValueError(f"sent {cmd}, got {resp}")
        cmd = b"R:0250\r\n"  # quarter wave retardation
        logger.debug(f"[PEM] setting retardation: {cmd}")
        self.ser.reset_input_buffer()
        self.ser.write(cmd)
        resp = self.ser.read(3)
        logger.debug(f"[PEM] received response: {cmd}")
        if resp != b"\n\r*":
            logger.error(f"[PEM] received response {resp}, expected '\\n\\r*'")
            raise ValueError(f"sent {cmd}, got {resp}")

    def disable_ret(self):
        cmd = b"I:1\r\n"
        logger.debug(f"[PEM] disabling retardation: {cmd}")
        self.ser.reset_input_buffer()
        self.ser.write(cmd)
        resp = self.ser.read(3)
        logger.debug(f"[PEM] received response: {cmd}")
        if resp != b"\n\r*":
            logger.error(f"[PEM] received response {resp}, expected '\\n\\r*'")
            raise ValueError(f"sent {cmd}, got {resp}")
