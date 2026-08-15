import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4


@dataclass
class Device:
    device_id: str
    name: str
    created_at: str
    status: str = "registered"
    metadata: Dict[str, Any] | None = None


class DeviceRegistry:
    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def _read(self) -> List[Dict[str, Any]]:
        if not self.storage_path.exists():
            return []
        with self.storage_path.open("r", encoding="utf-8") as handle:
            try:
                data = json.load(handle)
            except json.JSONDecodeError:
                return []
            return data if isinstance(data, list) else []

    def _write(self, devices: List[Dict[str, Any]]) -> None:
        with self.storage_path.open("w", encoding="utf-8") as handle:
            json.dump(devices, handle, indent=2)

    def list_devices(self) -> List[Dict[str, Any]]:
        return self._read()

    def register_device(self, name: str, metadata: Dict[str, Any] | None = None) -> Device:
        device_id = str(uuid4())
        device = Device(
            device_id=device_id,
            name=name,
            created_at=datetime.now(timezone.utc).isoformat(),
            status="registered",
            metadata=metadata or {},
        )
        devices = self._read()
        devices.append(asdict(device))
        self._write(devices)
        return device

    def get_device(self, device_id: str) -> Device | None:
        for entry in self._read():
            if entry.get("device_id") == device_id:
                return Device(**entry)
        return None
