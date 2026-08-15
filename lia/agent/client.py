import aiohttp
import json
import os
from pathlib import Path
from typing import Optional, Dict
from agent.crypto import CryptoStorage
from agent.config import AgentConfig

class LiaAgent:
    """
    Agent client for secondary device.
    
    Bootstrap flow:
    1. Read connection_file.json (provided by user)
    2. Validate connection file signature
    3. Connect to daemon URL
    4. Generate CSR and send to daemon
    5. Receive certificate from daemon
    6. Store certificate and establish mTLS connection
    7. Begin heartbeat loop
    """
    
    def __init__(self, config: AgentConfig):
        """
        Args:
            config: Agent configuration
        """
        self.config = config
        self.crypto = CryptoStorage(config.cert_storage_path)
        self.device_id: Optional[str] = None
        self.cluster_id: Optional[str] = None
        self.daemon_url: Optional[str] = None
    
    async def bootstrap_from_connection_file(self, connection_file_path: str) -> bool:
        """
        Load connection file and bootstrap device.
        
        Args:
            connection_file_path: Path to connection_file.json
        
        Returns:
            True if bootstrap successful
        """
        try:
            # Read connection file
            with open(connection_file_path, "r") as f:
                connection_data = json.load(f)
            
            # TODO: Verify connection file signature
            
            # Extract daemon info
            self.cluster_id = connection_data["cluster_id"]
            self.daemon_url = f"https://{connection_data['daemon_url']}"
            daemon_ca_cert = connection_data["daemon_ca_cert_pem"]
            connection_token = connection_data["connection_token"]
            
            # Store daemon CA certificate
            self.crypto.store_ca_certificate(daemon_ca_cert)
            
            # Bootstrap with daemon
            success = await self._register_with_daemon(connection_token)
            
            return success
        
        except Exception as e:
            print(f"Bootstrap failed: {e}")
            return False
    
    async def _register_with_daemon(self, connection_token: str) -> bool:
        """
        Register device with daemon and obtain certificate.
        
        Args:
            connection_token: Token from connection file
        
        Returns:
            True if registration successful
        """
        # Generate CSR
        csr_pem = self.crypto.generate_csr()
        
        async with aiohttp.ClientSession() as session:
            try:
                # TODO: Implement proper endpoint
                # For MVP, this is a placeholder
                response = await session.post(
                    f"{self.daemon_url}/api/v1/devices/register",
                    json={
                        "name": self.config.device_name,
                        "os_type": self.config.os_type,
                        "role": "secondary",
                        "connection_token": connection_token,
                        "csr_pem": csr_pem
                    }
                )
                
                if response.status == 201:
                    data = await response.json()
                    
                    # Store certificate
                    cert_pem = data["certificate_pem"]
                    private_key_pem = data["private_key_pem"]
                    
                    self.crypto.store_device_certificate(cert_pem)
                    self.crypto.store_device_private_key(private_key_pem)
                    
                    self.device_id = data["device_id"]
                    
                    return True
            
            except Exception as e:
                print(f"Registration error: {e}")
                return False
        
        return False
    
    async def heartbeat(self) -> bool:
        """
        Send heartbeat to daemon.
        
        Returns:
            True if heartbeat successful
        """
        # TODO: Implement with mTLS client certificate
        return True