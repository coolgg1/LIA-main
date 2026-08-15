import pytest
from daemon.services.connection_file import ConnectionFileManager
from datetime import datetime, timedelta

def test_generate_connection_file():
    """Connection file can be generated."""
    manager = ConnectionFileManager(secret_key="test-secret-key")
    
    conn_file = manager.generate_connection_file(
        cluster_id="cluster-uuid",
        device_name="My Phone",
        daemon_ca_cert_pem="-----BEGIN CERTIFICATE-----\n...",
        daemon_url="192.168.1.100:8443",
        valid_hours=24
    )
    
    assert conn_file["cluster_id"] == "cluster-uuid"
    assert conn_file["device_name"] == "My Phone"
    assert "hmac_signature" in conn_file
    assert "connection_token" in conn_file

def test_verify_connection_file_valid():
    """Valid connection file passes verification."""
    manager = ConnectionFileManager(secret_key="test-secret-key")
    
    conn_file = manager.generate_connection_file(
        cluster_id="cluster-uuid",
        device_name="My Phone",
        daemon_ca_cert_pem="cert",
        daemon_url="192.168.1.100:8443",
    )
    
    assert manager.verify_connection_file(conn_file) is True

def test_verify_connection_file_tampered():
    """Tampered connection file fails verification."""
    manager = ConnectionFileManager(secret_key="test-secret-key")
    
    conn_file = manager.generate_connection_file(
        cluster_id="cluster-uuid",
        device_name="My Phone",
        daemon_ca_cert_pem="cert",
        daemon_url="192.168.1.100:8443",
    )
    
    # Tamper with data
    conn_file["device_name"] = "Hacked Phone"
    
    assert manager.verify_connection_file(conn_file) is False

def test_connection_file_expiration():
    """Expired connection file is detected."""
    manager = ConnectionFileManager(secret_key="test-secret-key")
    
    # Create already-expired file
    conn_file = manager.generate_connection_file(
        cluster_id="cluster-uuid",
        device_name="My Phone",
        daemon_ca_cert_pem="cert",
        daemon_url="192.168.1.100:8443",
        valid_hours=-1  # Negative = already expired
    )
    
    assert manager.is_connection_file_expired(conn_file) is True