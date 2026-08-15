import pytest
from fastapi.testclient import TestClient
from daemon.main import app
from daemon.database import SessionLocal
from daemon.models.base import Base
from sqlalchemy import create_engine

@pytest.fixture
def client():
    """Create test client with in-memory database."""
    # Setup in-memory DB
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    
    # Override get_db dependency
    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    from daemon.database import get_db
    app.dependency_overrides[get_db] = override_get_db
    
    client = TestClient(app)
    yield client
    
    app.dependency_overrides.clear()

def test_health_check(client):
    """Health check endpoint responds."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_register_primary_device(client):
    """Primary device registration endpoint works."""
    response = client.post(
        "/api/v1/devices/register",
        json={
            "name": "My Workstation",
            "os_type": "linux",
            "role": "primary"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "device_id" in data
    assert "cluster_id" in data
    assert "certificate_pem" in data
    assert "private_key_pem" in data