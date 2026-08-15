from fastapi import FastAPI, HTTPException

from daemon.config import settings
from daemon.device import DeviceRegistry

app = FastAPI(title=settings.app_name)
registry = DeviceRegistry(settings.device_registry_path)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": settings.app_name, "port": settings.port}


@app.get("/devices")
def list_devices() -> list:
    return registry.list_devices()


@app.post("/devices/register")
def register_device(payload: dict) -> dict:
    name = payload.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="name is required")
    device = registry.register_device(name=name, metadata=payload.get("metadata", {}))
    return {
        "device_id": device.device_id,
        "name": device.name,
        "status": device.status,
        "created_at": device.created_at,
    }


@app.get("/devices/{device_id}")
def get_device(device_id: str) -> dict:
    device = registry.get_device(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="device not found")
    return {
        "device_id": device.device_id,
        "name": device.name,
        "status": device.status,
        "created_at": device.created_at,
        "metadata": device.metadata,
    }
