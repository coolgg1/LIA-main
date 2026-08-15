import os
from datetime import datetime, timedelta
from typing import Tuple
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtensionOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import hashlib

class CertificateManager:
    """Generate, sign, and validate mTLS certificates."""
    
    def __init__(self, ca_cert_path: str, ca_key_path: str):
        """
        Args:
            ca_cert_path: Path to CA certificate (PEM)
            ca_key_path: Path to CA private key (PEM)
        """
        self.ca_cert_path = ca_cert_path
        self.ca_key_path = ca_key_path
        self._load_ca_credentials()
    
    def _load_ca_credentials(self) -> None:
        """Load CA certificate and private key from disk."""
        if not os.path.exists(self.ca_cert_path) or not os.path.exists(self.ca_key_path):
            raise FileNotFoundError(
                f"CA certificate or key not found. "
                f"Run initialization task to generate CA."
            )
        
        with open(self.ca_cert_path, "rb") as f:
            self.ca_cert = x509.load_pem_x509_certificate(
                f.read(), default_backend()
            )
        
        with open(self.ca_key_path, "rb") as f:
            self.ca_key = serialization.load_pem_private_key(
                f.read(), password=None, backend=default_backend()
            )
    
    @staticmethod
    def generate_root_ca(
        common_name: str = "Lia Root CA",
        key_size: int = 2048,
        valid_days: int = 3650
    ) -> Tuple[x509.Certificate, rsa.RSAPrivateKey]:
        """
        Generate self-signed root CA certificate.
        
        Args:
            common_name: CA certificate CN field
            key_size: RSA key size (2048 or 4096)
            valid_days: Certificate validity period
        
        Returns:
            (ca_certificate, ca_private_key)
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=valid_days)
        ).add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        ).add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=True,
                crl_sign=True,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        ).sign(private_key, hashes.SHA256(), default_backend())
        
        return cert, private_key
    
    def generate_device_certificate(
        self,
        device_id: str,
        device_name: str,
        common_name: str,
        key_size: int = 2048,
        valid_days: int = 365
    ) -> Tuple[x509.Certificate, rsa.RSAPrivateKey]:
        """
        Generate a device certificate signed by CA.
        
        Args:
            device_id: Unique device UUID
            device_name: Human-readable device name
            common_name: Certificate CN field
            key_size: RSA key size
            valid_days: Validity period
        
        Returns:
            (device_certificate, device_private_key)
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        
        subject = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Lia"),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, device_id),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            self.ca_cert.subject
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=valid_days)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.RFC822Name(f"{device_name}@lia.local"),
            ]),
            critical=False,
        ).add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=True,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        ).add_extension(
            x509.ExtendedKeyUsage([
                x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH,
                x509.oid.ExtendedKeyUsageOID.SERVER_AUTH,
            ]),
            critical=True,
        ).sign(self.ca_key, hashes.SHA256(), default_backend())
        
        return cert, private_key
    
    @staticmethod
    def certificate_to_pem(cert: x509.Certificate) -> str:
        """Serialize certificate to PEM string."""
        return cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")
    
    @staticmethod
    def private_key_to_pem(key: rsa.RSAPrivateKey) -> str:
        """Serialize private key to PEM string (unencrypted)."""
        return key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode("utf-8")
    
    @staticmethod
    def get_certificate_thumbprint(cert_pem: str) -> str:
        """
        Compute SHA256 thumbprint of certificate.
        
        Args:
            cert_pem: Certificate in PEM format
        
        Returns:
            Hex-encoded SHA256 thumbprint
        """
        cert = x509.load_pem_x509_certificate(
            cert_pem.encode("utf-8"), default_backend()
        )
        thumbprint = hashlib.sha256(
            cert.public_bytes(serialization.Encoding.DER)
        ).hexdigest()
        return thumbprint
    
    def verify_certificate(self, cert_pem: str) -> bool:
        """
        Verify certificate is signed by this CA.
        
        Args:
            cert_pem: Certificate to verify (PEM format)
        
        Returns:
            True if certificate is valid and signed by CA
        """
        try:
            cert = x509.load_pem_x509_certificate(
                cert_pem.encode("utf-8"), default_backend()
            )
            # Verify signature was made with CA's public key
            self.ca_cert.public_key().verify(
                cert.signature,
                cert.tbs_certificate_bytes,
                padding.PKCS1v15(),
                cert.signature_hash_algorithm,
            )
            return True
        except Exception:
            return False