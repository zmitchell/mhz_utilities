import click
import logging
import logzero
import numpy as np
import struct
import serial
from enum import Enum
from logzero import logger
from math import floor
from pathlib import Path
from serial import Serial
from time import time, sleep
from ..equipment import LIA, PEM, Stepper


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


def get_calibration_table(path):
    table = {
        "wl": [],
        "wl_pem": [],
        "pos": [],
    }
    logger.debug(f"opening {path} to read calibration table")
    with open(path, "r") as file:
        for i, line in enumerate(file):
            wl_str, pos_str = line.strip().split(",")
            table["wl"].append(int(wl_str))
            table["wl_pem"].append(f"0{wl_str}0")
            table["pos"].append(int(pos_str))
    return table


def scan_interpolated(lia, pem, stepper, table, output_path, integration_time=1, wl_offset=None):
    pem.enable_ret()
    with open(output_path, "w") as file:
        file.write("wl,signal,noise,dc\n")
        for wl in range(795, 851, 1):
            logger.info(f"beginning collection for {wl}nm")
            if wl_offset is not None:
                wl_pem = f"0{wl + wl_offset}0"
            else:
                wl_pem = f"0{wl}0"
            # pos = interpolate_wl(wl, table)
            pos = interpolate_pos(table, wl)
            logger.debug(f"interpolated position {pos} for wavelength {wl}nm")
            stepper.move(pos)
            pem.set_wl(wl_pem)
            sleep(0.5)  # let the signal settle before adjusting the phase
            lia.auto_phase()
            samples = []
            logger.info("integrating")
            time_start = time()
            while (time() - time_start) < integration_time:
                samples.append(lia.data_snapshot())
            logger.info("processing samples")
            signal, noise, dc = average_samples(samples)
            result_line = f"{wl},{signal},{noise},{dc}\n"
            logger.debug(f"writing line to result file: {result_line}")
            file.write(result_line)
        logger.debug("sending the stepper to initial position")
        stepper.move(table["pos"][0]-2000)
    logger.debug("sending the stepper to initial position")
    stepper.move(table["pos"][0]-2000)


def scan(lia, pem, stepper, table, output_path, integration_time=1):
    pem.enable_ret()
    with open(output_path, "w") as file:
        for wl, wl_pem, pos in zip(table["wl"], table["wl_pem"], table["pos"]):
            logger.info(f"beginning collection for {wl}nm")
            stepper.move(pos)
            pem.set_wl(wl_pem)
            sleep(0.5)  # let the signal settle before adjusting the phase
            lia.auto_phase()
            samples = []
            logger.info("integrating")
            time_start = time()
            while (time() - time_start) < integration_time:
                samples.append(lia.data_snapshot())
            logger.info("processing samples")
            signal, noise, dc = average_samples(samples)
            result_line = f"{wl},{signal},{noise},{dc}\n"
            logger.debug(f"writing line to result file: {result_line}")
            file.write(result_line)
    logger.debug("sending the stepper to initial position")
    stepper.move(table["pos"][0]-2000)


def scan_computed(lia, pem, stepper, output_path, start_wl, stop_wl, integration_time=1):
    pem.enable_ret()
    with open(output_path, "w") as file:
        for wl in range(start_wl, stop_wl+1, 1):
            logger.info(f"beginning collection for {wl}nm")
            wl_pem = f"0{wl}0"
            pos = compute_pos(wl)
            logger.debug(f"computed position {pos} for wavelength {wl}nm")
            stepper.move(pos)
            pem.set_wl(wl_pem)
            sleep(0.5)  # let the signal settle before adjusting the phase
            lia.auto_phase()
            samples = []
            logger.info("integrating")
            time_start = time()
            while (time() - time_start) < integration_time:
                samples.append(lia.data_snapshot())
            logger.info("processing samples")
            signal, noise, dc = average_samples(samples)
            result_line = f"{wl},{signal},{noise},{dc}\n"
            logger.debug(f"writing line to result file: {result_line}")
            file.write(result_line)
    logger.debug("sending the stepper to initial position")
    stepper.move(compute_pos(start_wl)-2000)


def interpolate_wl(target_wl, table):
    if target_wl in table["wl"]:
        i = table["wl"].index(target_wl)
        return table["pos"][i]
    for i in range(len(table["wl"])-1):
        current_wl = table["wl"][i]
        next_wl = table["wl"][i+1]
        if (target_wl > current_wl) and (target_wl < next_wl):
            current_pos = table["pos"][i]
            next_pos = table["pos"][i+1]
            slope = (next_pos - current_pos) / (next_wl - current_wl)
            target_pos = floor(current_pos + (target_wl - current_wl) * slope)
            return target_pos


def interpolate_pos(table, wl):
    pos = 0
    if wl in table["wl"]:
        pos_index = table["wl"].index(wl)
        pos = table["pos"][pos_index]
    else:
        for i, (wl_lower, wl_upper) in enumerate(zip(table["wl"], table["wl"][1:])):
            if (wl > wl_lower) and (wl < wl_upper):
                pos_lower = table["pos"][i]
                pos_upper = table["pos"][i+1]
                slope = (pos_upper - pos_lower) / (wl_upper - wl_lower)
                wl_diff = wl - wl_lower
                pos = floor(pos_lower + slope * wl_diff)
                break
    if pos == 0:
        logger.error(f"[STEP] {wl}nm outside the calibration range")
        raise ValueError(f"{wl}nm outside of calibration range")
    logger.debug(f"[STEP] interpolated position {pos} for {wl}nm")
    return pos


def compute_pos(target_wl):
    def below_795(x):
        return floor(532.1996 * x - 3.6524)

    def at_or_above_795(x):
        return floor(194.8846 * x - 97096)

    if target_wl < 795:
        return below_795(target_wl)
    else:
        return at_or_above_795(target_wl)


def average_samples(samples):
    num_samples = len(samples)
    logger.debug(f"computing average of {num_samples} samples")
    ac_signals = np.ndarray(num_samples)
    dc_signals = np.ndarray(num_samples)
    for i, line in enumerate(samples):
        ac, _, _, dc = line.strip().split(",")
        ac_signals[i] = ac
        dc_signals[i] = dc
    avg_dc = dc_signals.mean()
    ac_corrected = np.ndarray(num_samples)
    for i, (ac, dc) in enumerate(zip(ac_signals, dc_signals)):
        scale_factor = avg_dc / dc
        ac_corrected[i] = ac * scale_factor
    signal = ac_corrected.mean()
    dc = dc_signals.mean()
    noise = ac_corrected.std()
    logger.debug(f"signal = {signal:.5e}, noise = {noise:.5e}")
    return signal, noise, dc


@click.command()
@click.option("-c", "--calibration-table", "table_path", type=click.Path(dir_okay=False), required=True)
@click.option("-o", "--output-folder", "folder", type=click.Path(file_okay=False, dir_okay=True), required=True)
@click.option("-s", "--stub", "stub")
@click.option("-t", "--integration-time", "int_time", type=click.FLOAT)
@click.option("-n", "--number-of-scans", "n", type=click.INT)
@click.option("-d", "--debug", "should_debug", type=click.BOOL, is_flag=True)
@click.option("--start", "start", type=click.INT)
@click.option("--stop", "stop", type=click.INT)
@click.option("--wavelength-offset", "wl_offset", type=click.INT)
def main(table_path, folder, stub, int_time, n, should_debug, start, stop, wl_offset):
    logzero.loglevel(logging.INFO)
    if should_debug:
        logzero.loglevel(logging.DEBUG)
    cal_table_path = Path.cwd() / table_path
    cal_table = get_calibration_table(cal_table_path)
    lia = LIA("COM4", ["X", "R", "XN", "IN3"])
    pem = PEM("COM3")
    stepper = Stepper("COM5")
    data_dir = Path.cwd() / folder
    data_dir.mkdir(exist_ok=True)
    scan_index = 0
    while True:
        if stub is not None:
            path = data_dir / f"{stub}_{scan_index:03}.csv"
        else:
            path = data_dir / f"scan_{scan_index:03}.csv"
        logger.info(f"starting iteration {scan_index + 1}")
        if (int_time is not None) and (int_time > 0):
            # scan(lia, pem, stepper, cal_table, path, integration_time=int_time)
            # scan_computed(lia, pem, stepper, path, 795, 860, integration_time=int_time)
            scan_interpolated(lia, pem, stepper, cal_table, path, integration_time=int_time, wl_offset=wl_offset)
        else:
            # scan(lia, pem, stepper, cal_table, path)
            # scan_computed(lia, pem, stepper, path, 795, 860)
            scan_interpolated(lia, pem, stepper, cal_table, path, wl_offset=wl_offset)
        scan_index += 1
        if (n is not None) and (scan_index >= n):
            break
    lia.ser.close()
    pem.ser.close()
    stepper.ser.close()


if __name__ == "__main__":
    main()
