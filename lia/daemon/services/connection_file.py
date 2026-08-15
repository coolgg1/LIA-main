import json
import os
from uuid import uuid4
from datetime import datetime, timedelta
import hmac
import hashlib
from typing import Dict, Optional

class ConnectionFileManager:
    """
    Generate and verify connection files for device bootstrap.
    
    Connection file format (JSON):
    {
      "cluster_id": "uuid-...",
      "device_name": "My Phone",
      "connection_token": "random-token-xyz",
      "daemon_ca_cert_pem": "-----BEGIN CERTIFICATE-----\n...",
      "daemon_url": "192.168.1.100:8443",
      "expires_at": "2024-01-22T10:30:00Z",
      "hmac_signature": "hex-encoded-hmac-sha256"
    }
    """
    
    def __init__(self, secret_key: str):
        """
        Args:
            secret_key: Secret used for HMAC signing (from environment)
        """
        self.secret_key = secret_key.encode("utf-8")
    
    def generate_connection_file(
        self,
        cluster_id: str,
        device_name: str,
        daemon_ca_cert_pem: str,
        daemon_url: str,
        valid_hours: int = 24
    ) -> Dict:
        """
        Generate a new connection file for secondary device bootstrap.
        
        Args:
            cluster_id: Cluster this device joins
            device_name: Name of device being added
            daemon_ca_cert_pem: CA certificate (PEM) for verification
            daemon_url: Daemon endpoint (IP:port)
            valid_hours: How long connection file is valid
        
        Returns:
            Dictionary with connection file data
        """
        connection_token = str(uuid4())
        expires_at = (datetime.utcnow() + timedelta(hours=valid_hours)).isoformat() + "Z"
        
        connection_data = {
            "cluster_id": cluster_id,
            "device_name": device_name,
            "connection_token": connection_token,
            "daemon_ca_cert_pem": daemon_ca_cert_pem,
            "daemon_url": daemon_url,
            "expires_at": expires_at,
        }
        
        # Sign the data (excluding signature field)
        signature = self._sign_data(connection_data)
        connection_data["hmac_signature"] = signature
        
        return connection_data
    
    def _sign_data(self, data: Dict) -> str:
        """
        HMAC-SHA256 sign connection file data.
        
        Args:
            data: Dictionary to sign (signature field must not be present)
        
        Returns:
            Hex-encoded HMAC-SHA256 signature
        """
        # Serialize consistently
        json_str = json.dumps(data, sort_keys=True, separators=(",", ":"))
        signature = hmac.new(
            self.secret_key,
            json_str.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def verify_connection_file(self, connection_file: Dict) -> bool:
        """
        Verify connection file is legitimate (not tampered).
        
        Args:
            connection_file: Connection file dictionary
        
        Returns:
            True if signature is valid
        """
        if "hmac_signature" not in connection_file:
            return False
        
        received_signature = connection_file["hmac_signature"]
        data_copy = {k: v for k, v in connection_file.items() if k != "hmac_signature"}
        
        expected_signature = self._sign_data(data_copy)
        
        # Constant-time comparison to prevent timing attacks
        return hmac.compare_digest(received_signature, expected_signature)
    
    def is_connection_file_expired(self, connection_file: Dict) -> bool:
        """
        Check if connection file has expired.
        
        Args:
            connection_file: Connection file dictionary
        
        Returns:
            True if expired
        """
        expires_at_str = connection_file.get("expires_at", "")
        try:
            # Parse ISO format datetime
            expires_at = datetime.fromisoformat(expires_at_str.replace("Z", "+00:00"))
            return datetime.utcnow() > expires_at
        except (ValueError, AttributeError):
            return True  # Invalid timestamp = expired