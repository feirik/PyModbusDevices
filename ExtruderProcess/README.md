# Extruder Simulator — Modbus TCP Server + HMI

A compact Modbus/TCP **extruder process simulator** (`main.py`) paired with a **tkinter HMI** (`hmi_tk.py`).

- **Server** simulates RPM, 3 barrel zones, melt temp, and pressure with simple first‑order dynamics.
- **HMI** provides START/STOP/RESET/E‑STOP, setpoints, live PVs, lightweight trends, and an HMI‑side production estimate (kg/h & total kg).

---

## Usage

### 1) Install

```bash
pip install "pymodbus==3.11.*"
```

### 2) Run the Simulator server

```bash
python extruder_server.py --port 5020 --log INFO
# Press ENTER in the server terminal to stop.
```

*Defaults:* `unit-id=1`.

### 3) Run the HMI (client)

```bash
python extruder_hmi.py --host 127.0.0.1 --port 5020 --unit-id 1
```

- Change setpoints and click **Apply Setpoints**.
- Use **START/STOP/RESET/E‑STOP**.
- Right column shows **Throughput (kg/h)** and **Total (kg)** (HMI‑side estimate).

---

## Dependencies

- **pymodbus** 3.11.\*


---

## Address Map

- **Coils (RW):** 0 START, 1 STOP, 2 RESET, 3 E‑STOP
- **Discrete Inputs (RO):** 0 RUNNING, 1 ALARM, 2 E‑STOP
- **Holding Regs (RW):** 0 SP\_RPM, 1..3 SP\_ZONE[1..3] (°C×10)
- **Input Regs (RO):** 0 PV\_RPM, 1..3 PV\_ZONE, 4 PV\_MELT, 5 PV\_PRESSURE
---

## License

This project depends on **pymodbus**, which is licensed under the **BSD 3‑Clause** license. When redistributing, ensure compliance with the BSD 3‑Clause terms for pymodbus. Your own code in this repository remains under your chosen license.
