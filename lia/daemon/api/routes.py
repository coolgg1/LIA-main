from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from daemon.models.device import DeviceRequest, DeviceResponse, Device
from daemon.services.device_registry import DeviceRegistry
from daemon.services.connection_file import ConnectionFileManager
from daemon.database import get_db
from sqlalchemy.orm import Session
from daemon.api.auth import get_current_device
from daemon.config import get_settings

router = APIRouter(prefix="/api/v1", tags=["devices"])

@router.post("/devices/register", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
async def register_device(
    request: DeviceRequest,
    db: Session = Depends(get_db),
    settings = Depends(get_settings)
):
    """
    Register a new primary or secondary device.
    
    For primary devices:
    - Generates new cluster
    - Returns device ID, certificate, private key, connection file URL
    
    For secondary devices:
    - Requires connection_token from connection file
    - Returns device ID and certificate (private key via one-time response only)
    """
    from daemon.services.crypto import CertificateManager
    
    cert_manager = CertificateManager(
        ca_cert_path=settings.ca_cert_path,
        ca_key_path=settings.ca_key_path
    )
    registry = DeviceRegistry(db, cert_manager)
    
    if request.role.value == "primary":
        device = registry.create_primary_device(
            name=request.name,
            os_type=request.os_type
        )
        
        # Generate connection file for this cluster
        connection_mgr = ConnectionFileManager(settings.connection_file_secret)
        connection_data = connection_mgr.generate_connection_file(
            cluster_id=device.cluster_id,
            device_name=request.name,
            daemon_ca_cert_pem=device.certificate_pem,
            daemon_url=settings.daemon_external_url,
        )
        
        return DeviceResponse(
            device_id=device.device_id,
            cluster_id=device.cluster_id,
            certificate_pem=device.certificate_pem,
            private_key_pem=device.private_key_pem,
            connection_file_url=f"https://{settings.daemon_external_url}/api/v1/devices/connection-file/{device.cluster_id}",
        )
    
    else:  # secondary
        # TODO: Extract and verify connection_token from request header
        # For now, simplified
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Secondary device registration requires connection token"
        )

@router.get("/devices", response_model=List[DeviceResponse])
async def list_devices(
    current_device: Device = Depends(get_current_device),
    db: Session = Depends(get_db),
):
    """List all devices in the current cluster."""
    from daemon.services.crypto import CertificateManager
    from daemon.config import get_settings
    
    settings = await get_settings()
    cert_manager = CertificateManager(
        ca_cert_path=settings.ca_cert_path,
        ca_key_path=settings.ca_key_path
    )
    registry = DeviceRegistry(db, cert_manager)
    
    devices = registry.get_devices_in_cluster(current_device.cluster_id)
    return [DeviceResponse.from_orm(d) for d in devices]

@router.get("/devices/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: str,
    current_device: Device = Depends(get_current_device),
    db: Session = Depends(get_db),
):
    """Retrieve a specific device."""
    from daemon.services.crypto import CertificateManager
    from daemon.config import get_settings
    
    settings = await get_settings()
    cert_manager = CertificateManager(
        ca_cert_path=settings.ca_cert_path,
        ca_key_path=settings.ca_key_path
    )
    registry = DeviceRegistry(db, cert_manager)
    
    device = registry.get_device_by_id(device_id)
    if not device or device.cluster_id != current_device.cluster_id:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return DeviceResponse.from_orm(device)