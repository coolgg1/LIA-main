from enum import Enum
from typing import Optional
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.sqlite import JSON
from pydantic import BaseModel, Field

Base = declarative_base()

class DeviceRole(str, Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"

class DeviceStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    UNREGISTERED = "unregistered"

class DeviceOS(str, Enum):
    LINUX = "linux"
    MACOS = "macos"
    WINDOWS = "windows"
    IOS = "ios"
    ANDROID = "android"

class Device(Base):
    """SQLAlchemy ORM model for devices."""
    __tablename__ = "devices"
    
    device_id = Column(String(36), primary_key=True)  # UUID
    cluster_id = Column(String(36), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    os_type = Column(String(50), nullable=False)  # "linux", "macos", "windows"
    role = Column(SQLEnum(DeviceRole), nullable=False)
    status = Column(SQLEnum(DeviceStatus), default=DeviceStatus.OFFLINE)
    certificate_thumbprint = Column(String(64), nullable=False, unique=True)
    certificate_pem = Column(String, nullable=False)  # Full cert for agent verification
    private_key_pem = Column(String, nullable=True)  # Only on primary device
    last_heartbeat = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    metadata = Column(JSON, default={})  # OS-specific info, capabilities

class DeviceRequest(BaseModel):
    """Request model for device registration."""
    name: str = Field(..., min_length=1, max_length=255)
    os_type: DeviceOS
    role: DeviceRole

class DeviceResponse(BaseModel):
    """Response model for device registration."""
    device_id: str
    cluster_id: str
    certificate_pem: str
    private_key_pem: Optional[str] = None  # Only for requesting device
    connection_file_url: Optional[str] = None  # Only for primary device
    
    class Config:
        from_attributes = True