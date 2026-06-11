import threading
import inspect

from pymodbus.client import ModbusTcpClient


class ModbusSession:
    def __init__(self, host, port, timeout, unit_id):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.unit_id = unit_id
        self._lock = threading.Lock()
        self._client = ModbusTcpClient(host, port=port, timeout=timeout)
        self._unit_id_keyword = self._get_unit_id_keyword()
        self._connect()

    def _get_unit_id_keyword(self):
        parameters = inspect.signature(self._client.read_coils).parameters
        if "device_id" in parameters:
            return "device_id"
        if "slave" in parameters:
            return "slave"
        if "unit" in parameters:
            return "unit"
        return None

    def _unit_id_argument(self):
        if self._unit_id_keyword is None:
            return {}
        return {self._unit_id_keyword: self.unit_id}

    def _connect(self):
        if not self._client.connect():
            raise ConnectionError(f"Could not connect to Modbus server {self.host}:{self.port}")

    def _ensure_connected(self):
        if not self._client.connected:
            self._connect()

    def read_coil(self, address):
        return self.read_coils(address, 1)[0]

    def read_coils(self, address, count):
        with self._lock:
            self._ensure_connected()
            result = self._client.read_coils(address, count=count, **self._unit_id_argument())
            if result.isError():
                raise RuntimeError(f"Read coils failed: {result}")
            return [int(value) for value in result.bits[:count]]

    def read_holding_registers(self, address, count):
        with self._lock:
            self._ensure_connected()
            result = self._client.read_holding_registers(address, count=count, **self._unit_id_argument())
            if result.isError():
                raise RuntimeError(f"Read holding registers failed: {result}")
            return result.registers

    def write_coil(self, address, value):
        with self._lock:
            self._ensure_connected()
            result = self._client.write_coil(address, bool(value), **self._unit_id_argument())
            return not result.isError()

    def write_register(self, address, value):
        with self._lock:
            self._ensure_connected()
            result = self._client.write_register(address, value, **self._unit_id_argument())
            return not result.isError()

    def close(self):
        self._client.close()
