from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from daemon.database import init_db
from daemon.api.routes import router
from daemon.config import get_settings
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="Lia Daemon",
    description="Device management and orchestration control plane",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # UI development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}

@app.on_event("startup")
async def startup():
    """Startup tasks."""
    logger.info("Lia daemon starting...")
    settings = get_settings()
    logger.info(f"Listening on {settings.daemon_host}:{settings.daemon_port}")