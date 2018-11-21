from serial import Serial
from logzero import logger


class LIA:
    def __init__(self, port, channels):
        self.ser = Serial(port, 115200, 8, 'N', 1, timeout=5)
        logger.info(f"[LIA] opened {port} for LIA")
        self.channels = channels
        self._set_data_channels()
        self._set_ref_source()
        self._set_grounding_mode()
        self._set_input_mode()
        self._set_input_coupling()
        self._set_voltage_input_mode()
        self._set_time_constant()
        self.filter_6db()

    def _set_data_channels(self):
        for i, channel in enumerate(self.channels):
            cmd = f"CDSP DAT{i+1},{channel}\n".encode("utf-8")
            logger.debug(f"[LIA] setting data channel {i} to {channel}: {cmd}")
            self.ser.write(cmd)

    def _set_ref_source(self):
        cmd = b"RSRC EXT\n"
        logger.debug(f"[LIA] setting external reference: {cmd}")
        self.ser.write(cmd)

    def _set_input_mode(self):
        cmd = b"IVMD VOLT\n"
        logger.debug(f"[LIA] setting input mode to voltage: {cmd}")
        self.ser.write(b"IVMD VOLT\n")

    def _set_input_coupling(self):
        cmd = b"ICPL AC\n"
        logger.debug(f"[LIA] setting AC input coupling: {cmd}")
        self.ser.write(cmd)

    def _set_voltage_input_mode(self):
        cmd = b"ISRC A\n"
        logger.debug(f"[LIA] setting voltage input to A: {cmd}")
        self.ser.write(cmd)

    def _set_grounding_mode(self):
        cmd = b"IGND FLO\n"
        logger.debug(f"[LIA] setting grounding mode to float: {cmd}")
        self.ser.write(cmd)

    def is_connected(self):
        logger.debug("[LIA] checking whether LIA is connected")
        logger.debug("[LIA] resetting input buffer")
        self.ser.reset_input_buffer()
        cmd = b"*IDN?\n"
        logger.debug(f"[LIA] getting LIA identification: {cmd}")
        self.ser.write(cmd)
        response = self.ser.read_until(size=45)
        logger.debug(f"[LIA] received response: (bytes) {response} (text) {response.decode()}")
        if response.decode() != "Stanford_Research_Systems,SR865A,003263,V1.47":
            logger.debug("[LIA] did not receive expected response, not connected")
            return False
        logger.debug("[LIA] received expected response, is connected")
        return True

    def _set_time_constant(self):
        # code = 12  # 1s
        code = 10  # 100ms
        cmd = f"OFLT {code}\n".encode('utf-8')
        logger.debug(f"[LIA] setting time constant: {cmd}")
        self.ser.write(cmd)

    def filter_6db(self):
        cmd = b"OFSL 0\n"
        logger.debug(f"[LIA] setting 6db filter slope: {cmd}")
        self.ser.write(cmd)

    def auto_phase(self):
        cmd = b"APHS\n"
        logger.debug(f"[LIA] setting phase with auto-phase: {cmd}")
        self.ser.write(cmd)

    def ac(self):
        logger.debug("[LIA] getting AC value")
        logger.debug("[LIA] resetting input buffer")
        self.ser.reset_input_buffer()
        cmd = b"OUTP? X\n"
        logger.debug(f"[LIA] querying AC value: {cmd}")
        self.ser.write(cmd)
        response_bytes = self.ser.read_until()  # read until newline
        response_str = response_bytes.decode()
        logger.debug(f"[LIA] received response: (bytes) {response_bytes} (text) {response_str}")
        return response_str

    def noise(self):
        logger.debug("[LIA] getting noise value")
        logger.debug("[LIA] resetting input buffer")
        self.ser.reset_input_buffer()
        cmd = b"OUTP? XN\n"
        logger.debug(f"[LIA] querying noise value: {cmd}")
        self.ser.write(cmd)
        response_bytes = self.ser.read_until()  # read until newline
        response_str = response_bytes.decode()
        logger.debug(f"[LIA] received response: (bytes) {response_bytes} (text) {response_str}")
        return response_str

    def signal_mag(self):
        logger.debug("[LIA] getting signal magnitude (R) value")
        logger.debug("[LIA] resetting input buffer")
        self.ser.reset_input_buffer()
        cmd = b"OUTP? R\n"
        logger.debug(f"[LIA] querying signal magnitude value: {cmd}")
        self.ser.write(cmd)
        response_bytes = self.ser.read_until()  # read until newline
        response_str = response_bytes.decode()
        logger.debug(f"[LIA] received response: (bytes) {response_bytes} (text) {response_str}")
        return response_str

    def dc(self):
        logger.debug("[LIA] getting DC value")
        logger.debug("[LIA] resetting input buffer")
        self.ser.reset_input_buffer()
        cmd = b"OUTP? IN3\n"
        logger.debug(f"[LIA] querying DC value: {cmd}")
        self.ser.write(cmd)
        response_bytes = self.ser.read_until()  # read until newline
        response_str = response_bytes.decode()
        logger.debug(f"[LIA] received response: (bytes) {response_bytes} (text) {response_str}")
        return response_str

    def data_snapshot(self):
        logger.debug("[LIA] getting snapshot values")
        logger.debug("[LIA] resetting input buffer")
        self.ser.reset_input_buffer()
        cmd = b"SNAPD?\n"
        logger.debug(f"[LIA] querying snapshot values: {cmd}")
        self.ser.write(cmd)
        response_bytes = self.ser.read_until(b"\r")  # read until newline
        response_str = response_bytes.decode()
        logger.debug(f"[LIA] received response: (bytes) {response_bytes} (text) {response_str}")
        return response_str
