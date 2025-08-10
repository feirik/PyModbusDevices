#!/usr/bin/env python3
"""
Extruder Simulator HMI (tkinter, pymodbus 3.11)
------------------------------------------------
Connects to the Extruder Simulator.

Run:
  pip install "pymodbus==3.11.*"
  python extruder_hmi.py --host 127.0.0.1 --port 5020 --unit-id 1
"""

import argparse
import queue
import threading
import time
from collections import deque
from typing import Deque, List, Optional

import tkinter as tk
from tkinter import ttk

from pymodbus.client import ModbusTcpClient

# =============================================================================
# Constants & Configuration
# =============================================================================
# Window
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768

# Polling
DEFAULT_POLL_MS = 1000  # UI poll/refresh interval
MIRROR_LOCK_S = 10     # time in seconds to suppress editor mirroring after Apply

# Address map (0-based)
COIL_START = 0
COIL_STOP = 1
COIL_RESET = 2
COIL_ESTOP = 3

DI_RUNNING = 0
DI_ALARM = 1
DI_ESTOP = 2

HR_SP_RPM = 0
HR_SP_Z1 = 1
HR_SP_Z2 = 2
HR_SP_Z3 = 3

IR_PV_RPM = 0
IR_PV_Z1 = 1
IR_PV_Z2 = 2
IR_PV_Z3 = 3
IR_PV_MELT = 4
IR_PV_PRESS = 5

# Scaling factors (Engineering unit <-> register)
S_TEMP = 10   # 0.1 °C
S_PRESS = 10  # 0.1 bar
S_SPEED = 1   # rpm

# High‑Performance HMI palette
PAL_GRAY = "#D5D5D5"
PAL_WHITE = "#FFFFFF"
PAL_LIGHT_GRAY = "#F3F3F3"
PAL_DARK_GRAY = "#888888"
PAL_DARKER_GRAY = "#4A4A4A"
PAL_BLACK = "#000000"
PAL_DARK_BLUE = "#0000D7"
PAL_DARK_GREEN = "#008000"
PAL_LIGHT_GREEN = "#99FF66"
PAL_LIGHT_BLUE = "#BBE0E3"
PAL_CYAN = "#00FFFF"
PAL_BROWN = "#CC6600"
PAL_PINK = "#FF99CC"
PAL_RED = "#FF0000"
PAL_YELLOW = "#FFFF00"
PAL_ORANGE = "#FF6600"
PAL_MAGENTA = "#FF00FF"
PAL_DARK_MAGENTA = "#CC0066"

# =============================================================================
# Helpers
# =============================================================================

def reg_to_eu(val: int, scale: int) -> float:
    """Register -> engineering units.

    For scale==1 we cast to float to keep a homogenous return type.
    """
    return (val / scale) if scale != 1 else float(val)


def eu_to_reg(val: float, scale: int) -> int:
    """Engineering units -> register with clamping to 16-bit unsigned."""
    v = int(round(val * scale)) if scale != 1 else int(round(val))
    return max(0, min(0xFFFF, v))

# =============================================================================
# UI widgets
# =============================================================================
class Led(ttk.Frame):
    """Tiny LED indicator drawn on a Canvas.

    Parameters
    ----------
    diameter : int
        Outer diameter in pixels.
    on, off : str
        Fill colors for ON/OFF states.
    """

    def __init__(self, master: tk.Misc, diameter: int = 20,
                 on: str = PAL_DARK_GREEN, off: str = PAL_DARK_GRAY) -> None:
        super().__init__(master)
        self.canvas = tk.Canvas(
            self,
            width=diameter,
            height=diameter,
            bd=0,
            highlightthickness=0,
            bg=PAL_LIGHT_GRAY,
        )
        self.canvas.pack()
        self._on, self._off = on, off
        self._oval = self.canvas.create_oval(
            2, 2, diameter - 2, diameter - 2,
            fill=self._off,
            outline=PAL_DARKER_GRAY,
        )
        self._state = False

        # Prevent the canvas from collapsing when packed tightly
        self.canvas.configure(height=diameter)

    def set(self, state: bool) -> None:
        """Update LED fill if state changed."""
        if state != self._state:
            self._state = state
            self.canvas.itemconfigure(self._oval, fill=(self._on if state else self._off))


class TrendCanvas(tk.Canvas):
    """Lightweight multi-trace trend without matplotlib.

    Traces: RPM, Melt °C, Pressure bar.
    """

    def __init__(self, master: tk.Misc, width: int = 680, height: int = 280,
                 max_points: int = 600) -> None:
        super().__init__(master, width=width, height=height,
                         bg=PAL_LIGHT_GRAY, highlightthickness=0, bd=0)
        self.max_points = max_points
        self.buf_rpm: Deque[float] = deque(maxlen=max_points)
        self.buf_melt: Deque[float] = deque(maxlen=max_points)
        self.buf_press: Deque[float] = deque(maxlen=max_points)

        # Colors
        self.col_grid = PAL_DARK_GRAY
        self.col_rpm = PAL_DARK_BLUE
        self.col_melt = PAL_BROWN
        self.col_press = PAL_ORANGE

        # Track current canvas size (tk keeps internal names we avoid)
        self._cw, self._ch = width, height
        self.bind("<Configure>", self._on_resize)
        self._draw_static()

    # ----- layout helpers -------------------------------------------------
    def _on_resize(self, ev: tk.Event) -> None:
        self._cw, self._ch = ev.width, ev.height
        self._draw_static()

    def _draw_static(self) -> None:
        """Grid + legend; re-drawn on resize."""
        self.delete("static")
        w, h = self._cw, self._ch

        # Grid
        sx = max(40, w // 16)
        sy = max(30, h // 10)
        for x in range(0, w + 1, sx):
            self.create_line(x, 0, x, h, fill=self.col_grid, tags="static")
        for y in range(0, h + 1, sy):
            self.create_line(0, y, w, y, fill=self.col_grid, tags="static")

        # Legend
        self.create_text(8, 10, text="RPM", anchor="w", fill=self.col_rpm, tags="static")
        self.create_text(60, 10, text="Melt °C", anchor="w", fill=self.col_melt, tags="static")
        self.create_text(140, 10, text="Pressure bar", anchor="w", fill=self.col_press, tags="static")

    # ----- data path ------------------------------------------------------
    def add_sample(self, rpm: float, melt_c: float, press_bar: float) -> None:
        """Append a sample and redraw."""
        self.buf_rpm.append(rpm)
        self.buf_melt.append(melt_c)
        self.buf_press.append(press_bar)
        self._redraw()

    @staticmethod
    def _scale(v: float, vmin: float, vmax: float, h: int) -> float:
        if vmax <= vmin:
            return h / 2.0
        return float(h) - (float(v) - float(vmin)) * (float(h) / (float(vmax) - float(vmin)))

    def _points(self, buf: Deque[float], vmin: float, vmax: float, w: int, h: int) -> List[float]:
        n = len(buf)
        if n < 2:
            return []
        step = max(1e-6, float(w) / float(n - 1))
        # last sample at right edge
        pts: List[float] = []
        for i, v in enumerate(buf):
            x = float(w) - (float(n - 1 - i) * step)
            y = self._scale(v, vmin, vmax, h)
            pts.extend((x, y))
        return pts

    def _redraw(self) -> None:
        self.delete("dyn")
        w, h = self._cw, self._ch
        if len(self.buf_rpm) < 2:
            return

        # Dynamic ranges with conservative clamps
        rpm_max_obs = max(self.buf_rpm) if self.buf_rpm else 400
        rpm_min, rpm_max = 0.0, min(400.0, max(50.0, rpm_max_obs * 1.1))

        if self.buf_melt:
            t_max_obs = max(self.buf_melt)
            t_min_obs = min(self.buf_melt)
        else:
            t_max_obs, t_min_obs = 200.0, 0.0
        t_min = max(0.0, t_min_obs - 5.0)
        t_max = min(350.0, max(50.0, t_max_obs + 5.0))

        if self.buf_press:
            p_max_obs = max(self.buf_press)
            p_min_obs = min(self.buf_press)
        else:
            p_max_obs, p_min_obs = 50.0, 0.0
        p_min = max(0.0, p_min_obs - 5.0)
        p_max = min(350.0, max(25.0, p_max_obs + 5.0))

        # Build polyline point lists
        rpm_pts = self._points(self.buf_rpm, rpm_min, rpm_max, w, h)
        melt_pts = self._points(self.buf_melt, t_min, t_max, w, h)
        press_pts = self._points(self.buf_press, p_min, p_max, w, h)

        # Draw polylines
        if len(rpm_pts) >= 4:
            self.create_line(*rpm_pts, fill=self.col_rpm, width=2, tags="dyn",
                             capstyle=tk.ROUND, joinstyle=tk.ROUND)
        if len(melt_pts) >= 4:
            self.create_line(*melt_pts, fill=self.col_melt, width=2, tags="dyn",
                             capstyle=tk.ROUND, joinstyle=tk.ROUND)
        if len(press_pts) >= 4:
            self.create_line(*press_pts, fill=self.col_press, width=2, tags="dyn",
                             capstyle=tk.ROUND, joinstyle=tk.ROUND)


# =============================================================================
# Modbus worker thread
# =============================================================================
class ModbusWorker(threading.Thread):
    """Background Modbus client poller.

    Sends write requests enqueued via `write_coil` / `write_hr` and periodically
    reads DI/IR/HR/Coils, pushing snapshots into `out_q` for the UI thread.
    """

    def __init__(self, host: str, port: int, unit: int,
                 period_ms: int, out_q: "queue.Queue[dict]") -> None:
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        self.unit = unit
        self.period = period_ms / 1000.0
        self.timeout = 2.0  # seconds
        self.out_q = out_q
        self.cmd_q: "queue.Queue[tuple]" = queue.Queue()
        self.stop_evt = threading.Event()
        self.client: Optional[ModbusTcpClient] = None
        self._first_connect_logged = False

    def run(self) -> None:
        while not self.stop_evt.is_set():
            try:
                if self.client is None:
                    self.client = ModbusTcpClient(self.host, port=self.port, timeout=self.timeout)

                if not self.client.is_socket_open():
                    if not self.client.connect() or not self.client.is_socket_open():
                        self.out_q.put({"connected": False})
                        time.sleep(0.5)
                        continue

                if not self._first_connect_logged:
                    print("[HMI] Connected TCP ->", self.host, self.port, "device_id=", self.unit)
                    self._first_connect_logged = True

                # Push a lightweight connection heartbeat (twice as in original)
                self.out_q.put({"connected": True})
                self.out_q.put({"connected": True})

                # Drain pending writes
                while True:
                    try:
                        kind, addr, value = self.cmd_q.get_nowait()
                    except queue.Empty:
                        break
                    if kind == "coil":
                        self.client.write_coil(address=addr, value=bool(value), device_id=self.unit)
                    elif kind == "hr":
                        self.client.write_register(address=addr, value=int(value), device_id=self.unit)

                # Periodic reads
                di = self.client.read_discrete_inputs(address=0, count=3, device_id=self.unit)
                ir = self.client.read_input_registers(address=0, count=6, device_id=self.unit)
                hr = self.client.read_holding_registers(address=0, count=4, device_id=self.unit)
                coils = self.client.read_coils(address=0, count=4, device_id=self.unit)

                if any(r.isError() for r in (di, ir, hr, coils)):
                    self.out_q.put({"connected": True, "error": "Read error"})
                else:
                    self.out_q.put({
                        "connected": True,
                        "di": list(getattr(di, "bits", []))[:3],
                        "ir": list(getattr(ir, "registers", []))[:6],
                        "hr": list(getattr(hr, "registers", []))[:4],
                        "coils": list(getattr(coils, "bits", []))[:4],
                    })

                time.sleep(self.period)

            except Exception as ex:
                # Push error to UI and print traceback for terminal debugging
                try:
                    import traceback, sys as _sys
                    print("[HMI] Modbus worker exception:", ex, file=_sys.stderr)
                    traceback.print_exc()
                except Exception:
                    pass
                self.out_q.put({"connected": False, "error": str(ex)})
                try:
                    if self.client:
                        self.client.close()
                except Exception:
                    pass
                self.client = None
                time.sleep(1.0)

        # Cleanup on stop
        try:
            if self.client:
                self.client.close()
        except Exception:
            pass

    # ---- async write API --------------------------------------------------
    def write_coil(self, addr: int, value: bool) -> None:
        self.cmd_q.put(("coil", addr, value))

    def write_hr(self, addr: int, value: int) -> None:
        self.cmd_q.put(("hr", addr, value))

    def stop(self) -> None:
        self.stop_evt.set()


# =============================================================================
# Main HMI window
# =============================================================================
class HMI(tk.Tk):
    """Application window with controls, indicators, PVs, trend, and production."""

    def __init__(self, host: str, port: int, unit: int, poll_ms: int,
                 kg_per_rev: float) -> None:
        super().__init__()
        self.title("Extruder Simulator HMI")
        self.configure(bg=PAL_LIGHT_GRAY)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        # After Apply, pause mirroring of SP editors so user edits aren't clobbered
        self._mirror_lock_until = 0.0

        # Production calc (HMI-side)
        self.kg_per_rev = max(0.0, float(kg_per_rev))
        self._last_integrate_ts: Optional[float] = None
        self.total_kg = 0.0

        # ttk styles (HP-HMI palette)
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("TFrame", background=PAL_LIGHT_GRAY)
        style.configure("TLabel", background=PAL_LIGHT_GRAY, foreground=PAL_DARKER_GRAY)
        style.configure("TButton", padding=8, background=PAL_LIGHT_GRAY, foreground=PAL_BLACK)
        try:
            style.configure("TButton", bordercolor=PAL_DARKER_GRAY, focusthickness=1, focuscolor=PAL_DARKER_GRAY)
            style.map("TButton", background=[("active", PAL_GRAY)])
            style.configure("TLabelframe", background=PAL_LIGHT_GRAY)
            style.configure("TLabelframe.Label", background=PAL_LIGHT_GRAY, foreground=PAL_DARKER_GRAY)
        except Exception:
            pass

        # ---- Layout (left/right columns) ---------------------------------
        root = ttk.Frame(self)
        root.pack(fill="both", expand=True, padx=12, pady=12)
        left = ttk.Frame(root)
        left.pack(side="left", fill="y")
        right = ttk.Frame(root)
        right.pack(side="right", fill="both", expand=True)

        # Connection
        frm_conn = ttk.LabelFrame(left, text="Connection")
        frm_conn.pack(fill="x", pady=(0, 30))
        self.lbl_conn = ttk.Label(frm_conn, text="Disconnected", foreground=PAL_RED)
        self.lbl_conn.pack(anchor="w", padx=10, pady=(8, 0))

        # Controls
        frm_ctl = ttk.LabelFrame(left, text="Controls")
        frm_ctl.pack(fill="x", pady=(0, 30))
        self.btn_start = ttk.Button(frm_ctl, text="START",
                                    command=lambda: self.write_coil(COIL_START, True))
        self.btn_stop = ttk.Button(frm_ctl, text="STOP",
                                   command=lambda: self.write_coil(COIL_STOP, True))
        self.btn_reset = ttk.Button(frm_ctl, text="RESET",
                                    command=lambda: self.write_coil(COIL_RESET, True))
        self.btn_estop = ttk.Button(frm_ctl, text="E-STOP",
                                    command=lambda: self.write_coil(COIL_ESTOP, True))
        for b in (self.btn_start, self.btn_stop, self.btn_reset, self.btn_estop):
            b.pack(fill="x", padx=10, pady=6)

        # Indicators
        frm_ind = ttk.LabelFrame(left, text="Indicators")
        frm_ind.pack(fill="x", pady=(0, 30))
        row = ttk.Frame(frm_ind)
        row.pack(fill="x", padx=10, pady=6)
        ttk.Label(row, text="RUNNING").pack(side="left")
        self.led_running = Led(row)
        self.led_running.pack(side="right")

        row = ttk.Frame(frm_ind)
        row.pack(fill="x", padx=10, pady=6)
        ttk.Label(row, text="ALARM").pack(side="left")
        self.led_alarm = Led(row, on=PAL_ORANGE)
        self.led_alarm.pack(side="right")

        row = ttk.Frame(frm_ind)
        row.pack(fill="x", padx=10, pady=6)
        ttk.Label(row, text="E-STOP").pack(side="left")
        self.led_estop = Led(row, on=PAL_RED)
        self.led_estop.pack(side="right")

        # Setpoints
        frm_sp = ttk.LabelFrame(left, text="Setpoints")
        frm_sp.pack(fill="x", pady=(0, 30))
        grid = ttk.Frame(frm_sp)
        grid.pack(fill="x", padx=10, pady=8)
        ttk.Label(grid, text="Screw RPM").grid(row=0, column=0, sticky="w")
        self.sp_rpm = tk.Spinbox(grid, from_=0, to=400, increment=5, width=7)
        self.sp_rpm.delete(0, "end")
        self.sp_rpm.insert(0, "120")
        self.sp_rpm.grid(row=0, column=1, sticky="e")

        ttk.Label(grid, text="Zone 1 °C").grid(row=1, column=0, sticky="w")
        self.sp_z1 = tk.Spinbox(grid, from_=0.0, to=350.0, increment=0.5, width=7)
        self.sp_z1.delete(0, "end")
        self.sp_z1.insert(0, "180.0")
        self.sp_z1.grid(row=1, column=1, sticky="e")

        ttk.Label(grid, text="Zone 2 °C").grid(row=2, column=0, sticky="w")
        self.sp_z2 = tk.Spinbox(grid, from_=0.0, to=350.0, increment=0.5, width=7)
        self.sp_z2.delete(0, "end")
        self.sp_z2.insert(0, "190.0")
        self.sp_z2.grid(row=2, column=1, sticky="e")

        ttk.Label(grid, text="Zone 3 °C").grid(row=3, column=0, sticky="w")
        self.sp_z3 = tk.Spinbox(grid, from_=0.0, to=350.0, increment=0.5, width=7)
        self.sp_z3.delete(0, "end")
        self.sp_z3.insert(0, "200.0")
        self.sp_z3.grid(row=3, column=1, sticky="e")

        ttk.Button(frm_sp, text="Apply Setpoints", command=self.apply_setpoints).pack(
            fill="x", padx=10, pady=(2, 10)
        )

        # PVs + Production (right-side column)
        frm_pv = ttk.LabelFrame(right, text="Process Values")
        frm_pv.pack(fill="x")
        grid = ttk.Frame(frm_pv)
        grid.pack(fill="x", padx=10, pady=8)

        self.lbl_rpm = ttk.Label(grid, text="0", font=("Segoe UI", 16, "bold"))
        self.lbl_z1 = ttk.Label(grid, text="0.0", font=("Segoe UI", 16, "bold"))
        self.lbl_z2 = ttk.Label(grid, text="0.0", font=("Segoe UI", 16, "bold"))
        self.lbl_z3 = ttk.Label(grid, text="0.0", font=("Segoe UI", 16, "bold"))
        self.lbl_melt = ttk.Label(grid, text="0.0", font=("Segoe UI", 16, "bold"))
        self.lbl_press = ttk.Label(grid, text="0.0", font=("Segoe UI", 16, "bold"))

        labels = [
            ("RPM", self.lbl_rpm),
            ("Zone1 °C", self.lbl_z1),
            ("Zone2 °C", self.lbl_z2),
            ("Zone3 °C", self.lbl_z3),
            ("Melt °C", self.lbl_melt),
            ("Pressure bar", self.lbl_press),
        ]
        for r, (name, wdg) in enumerate(labels):
            ttk.Label(grid, text=name).grid(row=r, column=0, sticky="w", padx=(0, 10))
            wdg.grid(row=r, column=1, sticky="e")

        # Vertical separator + production readouts
        sep = ttk.Separator(grid, orient="vertical")
        sep.grid(row=0, column=2, rowspan=len(labels), sticky="ns", padx=12)

        ttk.Label(grid, text="Thru kg/h").grid(row=0, column=3, sticky="w", padx=(0, 10))
        self.lbl_kgph = ttk.Label(grid, text="0.0", font=("Segoe UI", 16, "bold"))
        self.lbl_kgph.grid(row=0, column=4, sticky="e")

        ttk.Label(grid, text="Total kg").grid(row=1, column=3, sticky="w", padx=(0, 10))
        self.lbl_total = ttk.Label(grid, text="0.0", font=("Segoe UI", 16, "bold"))
        self.lbl_total.grid(row=1, column=4, sticky="e")

        # Trend
        frm_trend = ttk.LabelFrame(right, text="Trends (RPM / Melt °C / Pressure bar)")
        frm_trend.pack(fill="both", expand=True, pady=(8, 0))
        self.trend = TrendCanvas(frm_trend)
        self.trend.pack(fill="both", expand=True, padx=6, pady=6)

        # Worker & queue
        self.out_q: "queue.Queue[dict]" = queue.Queue()
        self.worker = ModbusWorker(host, port, unit, poll_ms, self.out_q)
        self.worker.start()
        self.after(50, self._drain)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ----- Actions -----------------------------------------------------------
    def write_coil(self, addr: int, value: bool) -> None:
        self.worker.write_coil(addr, value)

    def apply_setpoints(self) -> None:
        """Send setpoints from editors to server and pause UI mirroring."""
        def to_float(s: str) -> float:
            try:
                return float(s)
            except ValueError:
                return 0.0

        rpm = int(to_float(self.sp_rpm.get()))
        z1 = to_float(self.sp_z1.get())
        z2 = to_float(self.sp_z2.get())
        z3 = to_float(self.sp_z3.get())

        self.worker.write_hr(HR_SP_RPM, eu_to_reg(rpm, S_SPEED))
        self.worker.write_hr(HR_SP_Z1, eu_to_reg(z1, S_TEMP))
        self.worker.write_hr(HR_SP_Z2, eu_to_reg(z2, S_TEMP))
        self.worker.write_hr(HR_SP_Z3, eu_to_reg(z3, S_TEMP))

        # Hold off mirroring into editors so user edits aren't overwritten by next poll
        self._mirror_lock_until = time.time() + MIRROR_LOCK_S

    # ----- Queue -> UI ------------------------------------------------------
    def _drain(self) -> None:
        try:
            while True:
                payload = self.out_q.get_nowait()
                self._apply_payload(payload)
        except queue.Empty:
            pass
        self.after(50, self._drain)

    def _apply_payload(self, payload: dict) -> None:
        ok = payload.get("connected", False)
        self.lbl_conn.configure(text=("Connected" if ok else "Disconnected"),
                                foreground=(PAL_DARK_GREEN if ok else PAL_RED))
        if not ok:
            # Stop integrating while disconnected
            self._last_integrate_ts = None
            return

        # Indicators
        di = payload.get("di")
        if isinstance(di, (list, tuple)) and len(di) >= 3:
            self.led_running.set(bool(di[DI_RUNNING]))
            self.led_alarm.set(bool(di[DI_ALARM]))
            self.led_estop.set(bool(di[DI_ESTOP]))

        # Mirror HRs into editors when not during user edit/lockout
        hr = payload.get("hr")
        if (
            isinstance(hr, (list, tuple))
            and len(hr) >= 4
            and time.time() >= self._mirror_lock_until
            and self.focus_get() not in (self.sp_rpm, self.sp_z1, self.sp_z2, self.sp_z3)
        ):
            self.sp_rpm.delete(0, "end")
            self.sp_rpm.insert(0, str(int(reg_to_eu(hr[HR_SP_RPM], S_SPEED))))
            self.sp_z1.delete(0, "end")
            self.sp_z1.insert(0, f"{reg_to_eu(hr[HR_SP_Z1], S_TEMP):.1f}")
            self.sp_z2.delete(0, "end")
            self.sp_z2.insert(0, f"{reg_to_eu(hr[HR_SP_Z2], S_TEMP):.1f}")
            self.sp_z3.delete(0, "end")
            self.sp_z3.insert(0, f"{reg_to_eu(hr[HR_SP_Z3], S_TEMP):.1f}")

        # Process values + trends only when we have valid IRs
        ir = payload.get("ir")
        if not (isinstance(ir, (list, tuple)) and len(ir) >= 6):
            return
        rpm = reg_to_eu(ir[IR_PV_RPM], S_SPEED)
        z1 = reg_to_eu(ir[IR_PV_Z1], S_TEMP)
        z2 = reg_to_eu(ir[IR_PV_Z2], S_TEMP)
        z3 = reg_to_eu(ir[IR_PV_Z3], S_TEMP)
        melt = reg_to_eu(ir[IR_PV_MELT], S_TEMP)
        press = reg_to_eu(ir[IR_PV_PRESS], S_PRESS)

        self.lbl_rpm.configure(text=f"{rpm:.0f}")
        self.lbl_z1.configure(text=f"{z1:.1f}")
        self.lbl_z2.configure(text=f"{z2:.1f}")
        self.lbl_z3.configure(text=f"{z3:.1f}")
        self.lbl_melt.configure(text=f"{melt:.1f}")
        self.lbl_press.configure(text=f"{press:.1f}")

        self.trend.add_sample(rpm, melt, press)

        # --- Production calc (HMI-side) -----------------------------------
        kgph = self.kg_per_rev * float(rpm) * 60.0
        now = time.monotonic()
        if self._last_integrate_ts is not None:
            dt = max(0.0, now - self._last_integrate_ts)
            self.total_kg += kgph * dt / 3600.0
        self._last_integrate_ts = now

        self.lbl_kgph.configure(text=f"{kgph:0.1f}")
        self.lbl_total.configure(text=f"{self.total_kg:0.1f}")

    def _on_close(self) -> None:
        try:
            self.worker.stop()
        except Exception:
            pass
        self.after(150, self.destroy)


# =============================================================================
# CLI
# =============================================================================
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Extruder Simulator HMI (tkinter)")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=5020)
    ap.add_argument("--unit-id", type=int, default=1)
    ap.add_argument("--poll", type=int, default=DEFAULT_POLL_MS,
                    help=f"Poll period ms (default {DEFAULT_POLL_MS})")
    ap.add_argument("--kg-per-rev", type=float, default=0.004,
                    help="Estimated kg per screw revolution (default 0.004)")
    args = ap.parse_args()

    app = HMI(args.host, args.port, args.unit_id, args.poll, args.kg_per_rev)
    app.mainloop()
