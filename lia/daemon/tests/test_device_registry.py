import pytest
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from daemon.models.base import Base
from daemon.models.device import Device, DeviceRole
from daemon.services.device_registry import DeviceRegistry
from daemon.services.crypto import CertificateManager

@pytest.fixture
def db_session():
    """Create in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    yield db
    db.close()

@pytest.fixture
def cert_manager(tmp_path):
    """Create certificate manager with test CA."""
    ca_cert, ca_key = CertificateManager.generate_root_ca()
    ca_cert_pem = CertificateManager.certificate_to_pem(ca_cert)
    ca_key_pem = CertificateManager.private_key_to_pem(ca_key)
    
    ca_cert_file = tmp_path / "ca.crt"
    ca_key_file = tmp_path / "ca.key"
    ca_cert_file.write_text(ca_cert_pem)
    ca_key_file.write_text(ca_key_pem)
    
    return CertificateManager(str(ca_cert_file), str(ca_key_file))

def test_create_primary_device(db_session, cert_manager):
    """Primary device can be created."""
    registry = DeviceRegistry(db_session, cert_manager)
    
    device = registry.create_primary_device(
        name="My Workstation",
        os_type="linux"
    )
    
    assert device.device_id is not None
    assert device.cluster_id is not None
    assert device.role == DeviceRole.PRIMARY
    assert device.name == "My Workstation"
    assert device.certificate_pem is not None
    assert device.private_key_pem is not None

def test_get_device_by_id(db_session, cert_manager):
    """Device can be retrieved by ID."""
    registry = DeviceRegistry(db_session, cert_manager)
    
    device = registry.create_primary_device(
        name="My Workstation",
        os_type="linux"
    )
    
    retrieved = registry.get_device_by_id(device.device_id)
    assert retrieved is not None
    assert retrieved.device_id == device.device_id

def test_create_secondary_device(db_session, cert_manager):
    """Secondary device can be created in existing cluster."""
    registry = DeviceRegistry(db_session, cert_manager)
    
    primary = registry.create_primary_device(
        name="My Workstation",
        os_type="linux"
    )
    
    secondary = registry.create_secondary_device(
        cluster_id=primary.cluster_id,
        name="My Phone",
        os_type="android",
        connection_token="token-xyz"
    )
    
    assert secondary.device_id != primary.device_id
    assert secondary.cluster_id == primary.cluster_id
    assert secondary.role == DeviceRole.SECONDARY
    assert secondary.private_key_pem is None  # Never stored for secondary

def test_update_device_status(db_session, cert_manager):
    """Device status can be updated."""
    from daemon.models.device import DeviceStatus
    
    registry = DeviceRegistry(db_session, cert_manager)
    device = registry.create_primary_device(
        name="Test",
        os_type="linux"
    )
    
    updated = registry.update_device_status(device.device_id, DeviceStatus.ONLINE)
    
    assert updated.status == DeviceStatus.ONLINE
    assert updated.last_heartbeat is not None