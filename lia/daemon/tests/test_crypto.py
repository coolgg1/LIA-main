import pytest
import tempfile
import os
from daemon.services.crypto import CertificateManager
from cryptography import x509

def test_generate_root_ca():
    """Root CA certificate can be generated."""
    ca_cert, ca_key = CertificateManager.generate_root_ca()
    
    assert ca_cert is not None
    assert ca_key is not None
    assert ca_cert.subject.get_attributes_for_oid(x509.oid.NameOID.COMMON_NAME)[0].value == "Lia Root CA"

def test_certificate_to_pem():
    """Certificate can be serialized to PEM."""
    ca_cert, _ = CertificateManager.generate_root_ca()
    pem = CertificateManager.certificate_to_pem(ca_cert)
    
    assert pem.startswith("-----BEGIN CERTIFICATE-----")
    assert pem.endswith("-----END CERTIFICATE-----\n")

def test_private_key_to_pem():
    """Private key can be serialized to PEM."""
    _, ca_key = CertificateManager.generate_root_ca()
    pem = CertificateManager.private_key_to_pem(ca_key)
    
    assert pem.startswith("-----BEGIN PRIVATE KEY-----")
    assert pem.endswith("-----END PRIVATE KEY-----\n")

def test_certificate_thumbprint():
    """Certificate thumbprint is computed correctly."""
    ca_cert, _ = CertificateManager.generate_root_ca()
    pem = CertificateManager.certificate_to_pem(ca_cert)
    thumbprint = CertificateManager.get_certificate_thumbprint(pem)
    
    assert isinstance(thumbprint, str)
    assert len(thumbprint) == 64  # SHA256 hex = 64 chars

def test_device_certificate_generation(tmp_path):
    """Device certificate can be generated and signed by CA."""
    # Setup CA
    ca_cert, ca_key = CertificateManager.generate_root_ca()
    ca_cert_pem = CertificateManager.certificate_to_pem(ca_cert)
    ca_key_pem = CertificateManager.private_key_to_pem(ca_key)
    
    # Write to temp files
    ca_cert_file = tmp_path / "ca.crt"
    ca_key_file = tmp_path / "ca.key"
    ca_cert_file.write_text(ca_cert_pem)
    ca_key_file.write_text(ca_key_pem)
    
    # Create manager
    manager = CertificateManager(str(ca_cert_file), str(ca_key_file))
    
    # Generate device certificate
    dev_cert, dev_key = manager.generate_device_certificate(
        device_id="test-device-uuid",
        device_name="Test Device",
        common_name="test-device.lia.local"
    )
    
    assert dev_cert is not None
    assert dev_key is not None
    
    # Verify certificate subject
    cn = dev_cert.subject.get_attributes_for_oid(x509.oid.NameOID.COMMON_NAME)[0].value
    assert cn == "test-device.lia.local"