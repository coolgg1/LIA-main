import os
from typing import Any, Dict

import httpx


class DaemonClient:
    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or os.getenv("LIA_AGENT_ENDPOINT", "http://localhost:8000")
        self.client = httpx.Client(base_url=self.base_url, timeout=5.0)

    def heartbeat(self, agent_id: str, mode: str = "research") -> Dict[str, Any]:
        payload = {"agent_id": agent_id, "status": "online", "mode": mode}
        response = self.client.post("/agents/heartbeat", json=payload)
        response.raise_for_status()
        return response.json()

    def close(self) -> None:
        self.client.close()
