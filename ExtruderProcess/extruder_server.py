#!/usr/bin/env python3
"""
Extruder Simulator - Modbus TCP (pymodbus 3.11)
-----------------------------------------------
Minimal PLC-like Modbus TCP server for an extruder process.

USAGE:
  pip install "pymodbus==3.11.*"
  python extruder_server.py --port 5020 --log DEBUG
  (Press ENTER to stop)
"""

import argparse
import logging
import os
import random
import signal
import threading
import time
from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence

from pymodbus import ModbusDeviceIdentification
from pymodbus.datastore import (
    ModbusDeviceContext,
    ModbusSequentialDataBlock,
    ModbusServerContext,
)
from pymodbus.server import StartTcpServer

# --------------------------------------------------------------------------- #
# Constants & address map (logical 0-based)
# --------------------------------------------------------------------------- #

# Coils (RW)
COIL_START = 0
COIL_STOP  = 1
COIL_RESET = 2
COIL_ESTOP = 3

# Discrete Inputs (RO)
DI_RUNNING = 0
DI_ALARM   = 1
DI_ESTOP   = 2

# Holding Registers (RW)
HR_SP_RPM = 0
HR_SP_Z1  = 1
HR_SP_Z2  = 2
HR_SP_Z3  = 3

# Input Registers (RO)
IR_PV_RPM   = 0
IR_PV_Z1    = 1
IR_PV_Z2    = 2
IR_PV_Z3    = 3
IR_PV_MELT  = 4
IR_PV_PRESS = 5

# Datastore sizes (contiguous 1-based blocks)
COILS_SIZE   = 16
DISCRETE_SIZE= 16
HOLDING_SIZE = 64
INPUT_SIZE   = 64

# Scaling
S_TEMP  = 10   # 0.1 °C
S_PRESS = 10   # 0.1 bar
S_SPEED = 1    # rpm

# Behavior
COIL_AUTOCLEAR_S = 0.20  # FC05 pulse duration

# Convert a real-world value (°C/bar/rpm) to a 16-bit Modbus register using 'scale' (counts per unit), clamped to 0..65535.
def eu_to_reg(val: float, scale: int) -> int:
    """Engineering units -> register value (with clamp to 0..65535)."""
    v = int(round(val * scale)) if scale != 1 else int(round(val))
    return max(0, min(0xFFFF, v))

# Convert a 16-bit Modbus register back to a real-world value by dividing by 'scale' (counts per unit).
def reg_to_eu(val: int, scale: int) -> float:
    """Register value -> engineering units."""
    return (val / scale) if scale != 1 else float(val)


# --------------------------------------------------------------------------- #
# Minimal process model
# --------------------------------------------------------------------------- #

@dataclass
class Config:
    sp_rpm: float = 120.0
    sp_z1: float = 180.0
    sp_z2: float = 190.0
    sp_z3: float = 200.0
    tau_temp_s: float = 25.0
    tau_speed_s: float = 2.0
    k_press_rpm: float = 0.20
    k_press_temp: float = 0.10
    base_press: float = 15.0
    max_rpm: float = 400.0
    max_temp: float = 350.0
    overpress_bar: float = 250.0


class State:
    """Runtime state of the extruder process."""
    def __init__(self, cfg: Config):
        self.running = False
        self.alarm = False
        self.estop = False
        self.sp_rpm = cfg.sp_rpm
        self.sp_z: List[float] = [cfg.sp_z1, cfg.sp_z2, cfg.sp_z3]
        self.pv_rpm: float = 0.0
        self.pv_z: List[float] = [25.0, 25.0, 25.0]
        self.pv_melt: float = 25.0
        self.pv_press: float = 1.0


class Extruder:
    """Simple first-order process with a few couplings and noise."""
    def __init__(self, cfg: Config, rng: random.Random):
        self.cfg = cfg
        self.s = State(cfg)
        self.rng = rng
        self._press_f = cfg.base_press
        self._lock = threading.Lock()

    # Commands
    def cmd_start(self) -> None:
        with self._lock:
            if not self.s.estop:
                self.s.running = True
                self.s.alarm = False

    def cmd_stop(self) -> None:
        with self._lock:
            self.s.running = False

    def cmd_reset(self) -> None:
        with self._lock:
            self.s.alarm = False
            self.s.estop = False

    def cmd_estop(self) -> None:
        with self._lock:
            self.s.estop = True
            self.s.running = False
            self.s.alarm = True

    def set_sp(self, idx: int | str, value: float) -> None:
        """Setpoint write (rpm or zone index)."""
        with self._lock:
            if idx == "rpm":
                self.s.sp_rpm = max(0.0, min(self.cfg.max_rpm, value))
            else:
                i = int(idx)
                self.s.sp_z[i] = max(0.0, min(self.cfg.max_temp, value))

    # Dynamics
    def update(self, dt: float) -> None:
        """Advance simulated process by dt seconds."""
        c, s = self.cfg, self.s
        with self._lock:
            # Zones (first-order)
            alpha_t = min(1.0, dt / max(1e-3, c.tau_temp_s))
            for i in range(3):
                s.pv_z[i] += alpha_t * (s.sp_z[i] - s.pv_z[i]) + self.rng.gauss(0.0, 0.15)
                s.pv_z[i] = max(0.0, min(c.max_temp, s.pv_z[i]))

            # Melt temperature follows zones
            target_melt = 0.7 * sum(s.pv_z) / 3.0 + 0.3 * max(s.sp_z)
            s.pv_melt += alpha_t * (target_melt - s.pv_melt) + self.rng.gauss(0.0, 0.15)
            s.pv_melt = max(0.0, min(c.max_temp, s.pv_melt))

            # Speed (first-order to setpoint when running)
            if s.running and not s.estop:
                tgt = s.sp_rpm
                alpha_s = min(1.0, dt / max(1e-3, c.tau_speed_s))
                s.pv_rpm += alpha_s * (tgt - s.pv_rpm) + self.rng.gauss(0.0, 0.8)
                s.pv_rpm = max(0.0, min(c.max_rpm, s.pv_rpm))
            else:
                # Not running: hold exactly at 0, no noise
                s.pv_rpm = 0.0

            # Pressure (depends on rpm and melt temp)
            raw_p = c.base_press + c.k_press_rpm * s.pv_rpm + c.k_press_temp * max(0.0, s.pv_melt - 180.0)
            raw_p += self.rng.gauss(0.0, 0.8)
            alpha_p = min(1.0, dt / 1.0)
            self._press_f += alpha_p * (raw_p - self._press_f)
            s.pv_press = max(0.0, self._press_f)

            # Simple protection
            if s.pv_press > c.overpress_bar:
                s.alarm = True
                s.running = False


# --------------------------------------------------------------------------- #
# Datablock with write callback (1-based storage, 0-based logical callback)
# --------------------------------------------------------------------------- #

class CBBlock(ModbusSequentialDataBlock):
    """
    Contiguous block (start=1) that triggers a callback on client writes.
    Translates server address (1-based) -> logical address (0-based).
    """
    def __init__(self, values: Sequence[int], name: str, on_write=None):
        super().__init__(1, list(values))  # start at address 1
        self._name = name
        self._on_write = on_write
        self._suppress = False

    def setValues(self, address: int, values: int | Iterable[int]) -> None:  # signature required by base class
        super().setValues(address, values)
        if not self._suppress and self._on_write:
            try:
                vals = [values] if not isinstance(values, (list, tuple)) else list(values)
                logical = max(0, int(address) - 1)
                logging.debug("WRITE %s server@%s -> logical@%s v=%s", self._name, address, logical, vals)
                self._on_write(self._name, logical, vals)
            except Exception:
                logging.exception("Write-callback error for %s @%s", self._name, address)

    def setValues_no_cb(self, address: int, values: int | Iterable[int]) -> None:
        """Internal update without invoking the write callback."""
        self._suppress = True
        try:
            super().setValues(address, values)
        finally:
            self._suppress = False


# --------------------------------------------------------------------------- #
# Binder: maps coil/HR writes to Extruder commands/setpoints and pushes values
# --------------------------------------------------------------------------- #

class Binder:
    def __init__(self, extruder: Extruder,
                 co: CBBlock, di: ModbusSequentialDataBlock,
                 hr: CBBlock, ir: ModbusSequentialDataBlock):
        self.extruder = extruder
        self.co = co
        self.di = di
        self.hr = hr
        self.ir = ir

    def on_write(self, block_name: str, address0: int, values: List[int]) -> None:
        """Handle client writes. address0 is logical 0-based."""
        if block_name == "coils":
            logging.debug("COIL WRITE logical@%d -> %s", address0, values)
            for i, v in enumerate(values):
                a0 = address0 + i
                if a0 == COIL_START and v:
                    logging.warning("START command accepted (coil logical %d)", COIL_START)
                    self.extruder.cmd_start()
                    self.push()
                    threading.Timer(COIL_AUTOCLEAR_S, lambda aa=a0: self.co.setValues_no_cb(aa + 1, [0])).start()
                elif a0 == COIL_STOP and v:
                    logging.warning("STOP command accepted (coil logical %d)", COIL_STOP)
                    self.extruder.cmd_stop()
                    self.push()
                    threading.Timer(COIL_AUTOCLEAR_S, lambda aa=a0: self.co.setValues_no_cb(aa + 1, [0])).start()
                elif a0 == COIL_RESET and v:
                    logging.warning("RESET command accepted (coil logical %d)", COIL_RESET)
                    self.extruder.cmd_reset()
                    self.push()
                    threading.Timer(COIL_AUTOCLEAR_S, lambda aa=a0: self.co.setValues_no_cb(aa + 1, [0])).start()
                elif a0 == COIL_ESTOP and v:
                    logging.warning("E-STOP command accepted (coil logical %d)", COIL_ESTOP)
                    self.extruder.cmd_estop()
                    self.push()

        elif block_name == "holding":
            logging.debug("HR WRITE logical@%d -> %s", address0, values)
            for i, raw in enumerate(values):
                a0 = address0 + i
                if a0 == HR_SP_RPM:
                    self.extruder.set_sp("rpm", reg_to_eu(raw, S_SPEED))
                elif a0 in (HR_SP_Z1, HR_SP_Z2, HR_SP_Z3):
                    self.extruder.set_sp(a0 - HR_SP_Z1, reg_to_eu(raw, S_TEMP))

    def push(self) -> None:
        """Push current state into DI/IR/HR blocks (server 1-based)."""
        s = self.extruder.s
        # Discrete Inputs
        self.di.setValues(1, [
            1 if s.running else 0,
            1 if s.alarm else 0,
            1 if s.estop else 0,
        ])
        # Input Registers
        self.ir.setValues(1, [eu_to_reg(s.pv_rpm, S_SPEED)])
        self.ir.setValues(2, [eu_to_reg(s.pv_z[0], S_TEMP)])
        self.ir.setValues(3, [eu_to_reg(s.pv_z[1], S_TEMP)])
        self.ir.setValues(4, [eu_to_reg(s.pv_z[2], S_TEMP)])
        self.ir.setValues(5, [eu_to_reg(s.pv_melt, S_TEMP)])
        self.ir.setValues(6, [eu_to_reg(s.pv_press, S_PRESS)])

        # Holding Registers (mirror setpoints without triggering callbacks)
        self.hr.setValues_no_cb(1, [eu_to_reg(s.sp_rpm, S_SPEED)])
        self.hr.setValues_no_cb(2, [eu_to_reg(s.sp_z[0], S_TEMP)])
        self.hr.setValues_no_cb(3, [eu_to_reg(s.sp_z[1], S_TEMP)])
        self.hr.setValues_no_cb(4, [eu_to_reg(s.sp_z[2], S_TEMP)])


# --------------------------------------------------------------------------- #
# Update loop thread
# --------------------------------------------------------------------------- #

class UpdateThread(threading.Thread):
    """Periodic process update + push to datastore."""
    def __init__(self, extruder: Extruder, binder: Binder, period: float):
        super().__init__(daemon=True)
        self.extruder = extruder
        self.binder = binder
        self.period = period
        self.stop_evt = threading.Event()

    def run(self) -> None:
        last = time.monotonic()
        while not self.stop_evt.is_set():
            now = time.monotonic()
            dt = now - last
            last = now
            try:
                self.extruder.update(dt)
                self.binder.push()
            except Exception:
                logging.exception("Update loop error")
            time.sleep(max(0.0, self.period))

    def stop(self) -> None:
        self.stop_evt.set()


# --------------------------------------------------------------------------- #
# Bootstrap
# --------------------------------------------------------------------------- #

def main() -> None:
    ap = argparse.ArgumentParser(description="Extruder Simulator (pymodbus 3.11)")
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=5020)
    ap.add_argument("--unit-id", type=int, default=1)
    ap.add_argument("--period", type=float, default=0.2)
    ap.add_argument("--log", default="INFO")
    args = ap.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    rng = random.Random()

    # Datastore (all blocks are 1-based)
    binder_ref: dict[str, Binder] = {}

    co_block = CBBlock([0] * COILS_SIZE, name="coils",
                       on_write=lambda *a, **k: binder_ref["b"].on_write(*a, **k))
    di_block = ModbusSequentialDataBlock(1, [0] * DISCRETE_SIZE)
    hr_block = CBBlock([0] * HOLDING_SIZE, name="holding",
                       on_write=lambda *a, **k: binder_ref["b"].on_write(*a, **k))
    ir_block = ModbusSequentialDataBlock(1, [0] * INPUT_SIZE)

    device = ModbusDeviceContext(di=di_block, co=co_block, hr=hr_block, ir=ir_block)
    context = ModbusServerContext(devices={args.unit_id: device}, single=False)

    # Process + binder
    extruder = Extruder(Config(), rng)
    binder = Binder(extruder, co_block, di_block, hr_block, ir_block)
    binder_ref["b"] = binder

    # Identity
    identity = ModbusDeviceIdentification()
    identity.VendorName = "ExtruderSim"
    identity.ProductCode = "EXSIM"
    identity.ProductName = "Extruder Simulator"
    identity.ModelName = "Extruder PLC (Modbus TCP)"
    identity.MajorMinorRevision = "1.0"

    # Update loop
    updater = UpdateThread(extruder, binder, args.period)
    updater.start()

    # Ctrl-C: stop gracefully
    def _sigint(_sig, _frm):
        logging.info("Shutting down (SIGINT)...")
        updater.stop()
        os._exit(0)

    signal.signal(signal.SIGINT, _sigint)

    # ENTER-to-exit helper
    def _wait_for_enter():
        logging.info("Press ENTER to stop the server...")
        try:
            input()
        except EOFError:
            return
        logging.info("ENTER received, stopping.")
        updater.stop()
        os._exit(0)

    threading.Thread(target=_wait_for_enter, daemon=True).start()

    logging.info("Listening on %s:%d (unit %d)",
                 args.host, args.port, args.unit_id)

    StartTcpServer(context, identity=identity, address=(args.host, args.port))


if __name__ == "__main__":
    main()
