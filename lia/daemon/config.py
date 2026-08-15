from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredential
from sqlalchemy.orm import Session
from daemon.models.device import Device
from daemon.database import get_db
import ssl

security = HTTPBearer()

async def get_current_device(
    credentials: HTTPAuthCredential = Depends(security),
    db: Session = Depends(get_db),
) -> Device:
    """
    Verify mTLS client certificate and return authenticated device.
    
    In production, FastAPI/Uvicorn should be configured with:
    - ssl_certfile=daemon.crt
    - ssl_keyfile=daemon.key
    - ssl_ca_certs=ca.crt (for client verification)
    - ssl_cert_reqs=ssl.CERT_REQUIRED
    
    This middleware receives certificate info from SSL layer.
    """
    # TODO: Extract certificate from SSL connection info
    # For MVP Phase 0, use simple token-based auth
    # Phase 1 upgrade to proper mTLS
    
    token = credentials.credentials
    device = db.query(Device).filter(
        Device.certificate_thumbprint == token
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid certificate"
        )
    
    return device