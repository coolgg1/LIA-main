import pytest
from daemon.models.device import Device, DeviceRole, DeviceStatus
from datetime import datetime

def test_device_creation():
    """Device model can be instantiated."""
    device = Device(
        device_id="test-uuid",
        cluster_id="cluster-uuid",
        name="Test Device",
        os_type="linux",
        role=DeviceRole.PRIMARY,
        certificate_thumbprint="abc123",
        certificate_pem="-----BEGIN CERTIFICATE-----\n...",
    )
    assert device.name == "Test Device"
    assert device.role == DeviceRole.PRIMARY
    assert device.status == DeviceStatus.OFFLINE

def test_device_role_enum():
    """Device roles are properly enumerated."""
    assert DeviceRole.PRIMARY.value == "primary"
    assert DeviceRole.SECONDARY.value == "secondary"

def test_device_status_tracking():
    """Device status can be updated."""
    device = Device(
        device_id="test-uuid",
        cluster_id="cluster-uuid",
        name="Test",
        os_type="linux",
        role=DeviceRole.PRIMARY,
        certificate_thumbprint="abc",
        certificate_pem="...",
    )
    device.status = DeviceStatus.ONLINE
    assert device.status == DeviceStatus.ONLINE