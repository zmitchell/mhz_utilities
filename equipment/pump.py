from logzero import logger
from serial import Serial
import sys

class Pump:
    def __init__(self, port_name):
        self.ser = Serial(port_name,
                          timeout=5,
                          baudrate=115_200,)
        logger.info(f"[PUMP] opened {port_name} for pump")

    def turn_on(self):
        msg = b"ON\n"
        logger.debug(f"[PUMP] turning the power on: {msg}")
        self.ser.write(msg)

    def turn_off(self):
        msg = b"OFF\n"
        logger.debug(f"[PUMP] turning the power off: {msg}")
        self.ser.write(msg)

    def open_shutter(self):
        msg = b"SHT:1\n"
        logger.debug(f"[PUMP] opening the shutter: {msg}")
        self.ser.write(msg)

    def close_shutter(self):
        msg = b"SHT:0\n"
        logger.debug(f"[PUMP] closing the shutter: {msg}")
        self.ser.write(msg)

    def set_power(self, watts):
        msg = f"P:{watts}\n".encode("utf-8")
        logger.debug(f"[PUMP] setting the pump power: {msg}")
        self.ser.write(msg)

    def diode_is_on(self):
        msg = b"?D\n"
        logger.debug(f"[PUMP] querying diode power state: {msg}")
        self.ser.reset_input_buffer()
        self.ser.write(msg)
        resp = self.ser.read(2)
        if (resp != b"1\n") and (resp != b"0\n"):
            logger.error(f"[PUMP] received response {resp}, expected b'1\\n' or b'0\\n'")
            sys.exit(1)
        is_on = resp == b"1\n"
        if is_on:
            logger.debug("[PUMP] the diode is emitting")
        else:
            logger.debug("[PUMP] the diode is not emitting")
        return is_on

    def shutter_is_open(self):
        msg = b"?SHT\n"
        logger.debug(f"[PUMP] querying shutter state: {msg}")
        self.ser.reset_input_buffer()
        self.ser.write(msg)
        resp = self.ser.read(2)
        if (resp != b"1\n") and (resp != b"0\n"):
            logger.error(f"[PUMP] received response {resp}, expected b'1\\n' or b'0\\n'")
            sys.exit(1)
        is_open = resp == b"1\n"
        if is_open:
            logger.debug("[PUMP] the shutter is open")
        else:
            logger.debug("[PUMP] the shutter is closed")
        return is_open

    def current_power(self):
        msg = b"?P\n"
        logger.debug(f"[PUMP] querying diode output power: {msg}")
        self.ser.reset_input_buffer()
        self.ser.write(msg)
        resp = self.ser.read_until()
        resp_data = resp.decode().strip()
        if not resp_data.isdecimal():
            logger.error(f"[PUMP] received {resp_data}, expected float 0<=f<=5.0")
            sys.exit(1)
        power = float(resp_data)
        logger.debug(f"[PUMP] the output power is {power:.3f}")
        return power
