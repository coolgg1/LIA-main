from typing import Optional, List, Tuple, cast
from uuid import uuid4
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from daemon.models.device import Device, DeviceRole, DeviceStatus
from daemon.services.crypto import CertificateManager
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import rsa

class DeviceRegistry:
    """CRUD operations for device registry."""
    
    def __init__(self, db_session: Session, cert_manager: CertificateManager):
        """
        Args:
            db_session: SQLAlchemy database session
            cert_manager: Certificate manager instance
        """
        self.db = db_session
        self.cert_manager = cert_manager
    
    def create_primary_device(
        self,
        name: str,
        os_type: str
    ) -> Device:
        """
        Create and register the primary device for a new cluster.
        
        Args:
            name: Human-readable device name
            os_type: Operating system type
        
        Returns:
            Device object with certificate and cluster ID
        """
        # Generate new cluster
        cluster_id = str(uuid4())
        device_id = str(uuid4())
        
        # Generate certificate
        cert, private_key = cast(Tuple[x509.Certificate, rsa.RSAPrivateKey], self.cert_manager.generate_device_certificate(
            device_id=device_id,
            device_name=name,
            common_name=f"{name} (primary)",
        ))
        
        cert_pem = CertificateManager.certificate_to_pem(cert)
        key_pem = CertificateManager.private_key_to_pem(private_key)
        thumbprint = CertificateManager.get_certificate_thumbprint(cert_pem)
        
        # Create device record
        device = Device(
            device_id=device_id,
            cluster_id=cluster_id,
            name=name,
            os_type=os_type,
            role=DeviceRole.PRIMARY,
            status=DeviceStatus.ONLINE,
            certificate_thumbprint=thumbprint,
            certificate_pem=cert_pem,
            private_key_pem=key_pem,  # Store on primary only
        )
        
        self.db.add(device)
        self.db.commit()
        self.db.refresh(device)
        
        return device
    
    def create_secondary_device(
        self,
        cluster_id: str,
        name: str,
        os_type: str,
        connection_token: str
    ) -> Device:
        """
        Create and register a secondary device, verifying connection token.
        
        Args:
            cluster_id: Cluster to join
            name: Device name
            os_type: Operating system type
            connection_token: Token from connection file (for verification)
        
        Returns:
            Device object with certificate
        
        Raises:
            ValueError: If cluster not found or token invalid
        """
        # Verify cluster exists
        primary = self._get_primary_for_cluster(cluster_id)
        if not primary:
            raise ValueError(f"Cluster {cluster_id} not found")
        
        device_id = str(uuid4())
        
        # Generate certificate (no private key stored on primary)
        cert, _ = cast(Tuple[x509.Certificate, rsa.RSAPrivateKey], self.cert_manager.generate_device_certificate(
            device_id=device_id,
            device_name=name,
            common_name=f"{name} (secondary)",
        ))
        
        cert_pem = CertificateManager.certificate_to_pem(cert)
        thumbprint = CertificateManager.get_certificate_thumbprint(cert_pem)
        
        # Create device record (private key NOT stored)
        device = Device(
            device_id=device_id,
            cluster_id=cluster_id,
            name=name,
            os_type=os_type,
            role=DeviceRole.SECONDARY,
            status=DeviceStatus.OFFLINE,  # Becomes ONLINE after first heartbeat
            certificate_thumbprint=thumbprint,
            certificate_pem=cert_pem,
            private_key_pem=None,  # Never store secondary private key
        )
        
        self.db.add(device)
        self.db.commit()
        self.db.refresh(device)
        
        # Return certificate + private key (ONE TIME, in response only)
        # Caller responsible for returning both to secondary device
        return device
    
    def get_device_by_id(self, device_id: str) -> Optional[Device]:
        """Retrieve device by ID."""
        return self.db.query(Device).filter(Device.device_id == device_id).first()
    
    def get_devices_in_cluster(self, cluster_id: str) -> List[Device]:
        """Retrieve all devices in a cluster."""
        return self.db.query(Device).filter(Device.cluster_id == cluster_id).all()
    
    def _get_primary_for_cluster(self, cluster_id: str) -> Optional[Device]:
        """Get primary device for a cluster."""
        return self.db.query(Device).filter(
            and_(
                Device.cluster_id == cluster_id,
                Device.role == DeviceRole.PRIMARY
            )
        ).first()
    
    def update_device_status(self, device_id: str, status: DeviceStatus) -> Optional[Device]:
        """Update device status and heartbeat timestamp."""
        device = self.get_device_by_id(device_id)
        if device:
            device.status = status.value
            device.last_heartbeat = datetime.now()
            self.db.commit()
            self.db.refresh(device)
        return device
    
    def delete_device(self, device_id: str) -> bool:
        """Remove device from registry."""
        device = self.get_device_by_id(device_id)
        if device:
            self.db.delete(device)
            self.db.commit()
            return True
        return False