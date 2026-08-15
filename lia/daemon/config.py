import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = "lia-daemon"
    host: str = os.getenv("LIA_HOST", "0.0.0.0")
    port: int = int(os.getenv("LIA_PORT", "8000"))
    log_level: str = os.getenv("LIA_LOG_LEVEL", "INFO")
    device_registry_path: str = os.getenv("LIA_DEVICE_REGISTRY_PATH", "./data/devices.json")
    tls_cert_path: str = os.getenv("LIA_TLS_CERT_PATH", "./certs/server.crt")
    tls_key_path: str = os.getenv("LIA_TLS_KEY_PATH", "./certs/server.key")
    ca_cert_path: str = os.getenv("LIA_CA_CERT_PATH", "./certs/ca.crt")


settings = Settings()
