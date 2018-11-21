import click
import logzero
import logging
import struct
from enum import Enum
from logzero import logger
from math import floor
from serial import Serial


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


@click.command()
@click.argument("pos", type=click.INT)
def main(pos):
    logzero.loglevel(logging.INFO)
    stepper = Stepper("COM5")
    stepper.move(pos)
    stepper.ser.close()


@click.group()
def cli():
    return


@cli.command()
@click.argument("pos", type=click.INT)
def abs(pos):
    logzero.loglevel(logging.INFO)
    stepper = Stepper("COM5")
    stepper.move(pos)
    stepper.ser.close()


@cli.command()
@click.argument("cal_file", type=click.File())
@click.argument("wl", type=click.INT)
def interpolate(cal_file, wl):
    logzero.loglevel(logging.INFO)
    cal_table = get_calibration_table(cal_file)
    pos = interpolate_pos(cal_table, wl)
    stepper = Stepper("COM5")
    stepper.move(pos - 2000)
    stepper.move(pos)
    stepper.ser.close()
    cal_file.close()


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


def get_calibration_table(file):
    table = {
        "wl": [],
        "pos": [],
    }
    for i, line in enumerate(file):
        wl_str, pos_str = line.strip().split(",")
        table["wl"].append(int(wl_str))
        table["pos"].append(int(pos_str))
    return table


if __name__ == "__main__":
    cli()
