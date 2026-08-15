# Lia Architecture

## Deployment Model: Daemon + Agent

Lia is NOT a bare-metal hypervisor (yet). MVP is a system-level control plane:

- **Primary Daemon:** Runs on primary device (privileged service)
  - Device registry and cluster management
  - Workspace and mode orchestration
  - Search bar command routing
  - Cross-device policy enforcement
  - Telemetry and logging

- **Secondary Agent:** Runs on secondary devices (lightweight client)
  - Connects to daemon via mTLS
  - Receives mode directives (concentration, research, etc.)
  - Reports device status and compliance
  - Executes local restrictions

## Technology Stack Rationale

| Component | Choice | Why |
|-----------|--------|-----|
| Daemon | Python 3.11 + FastAPI | Async HTTP, fast iteration, rich ecosystem (cryptography, psutil) |
| Agent | Python 3.11 + aiohttp | Same ecosystem, simple deployment |
| UI | React 18 + TypeScript | Type-safe components, Electron optional Phase 2 |
| Protocol | JSON/HTTPS + mTLS | Simple debugging, human-readable logs, web-native |
| Storage | SQLite | No external DB dependency, sufficient for single-primary |
| Testing | pytest + Vitest | Mature, excellent async support, fast execution |

### Why NOT...
- **Rust daemon:** Slower iteration, harder hiring
- **Node.js daemon:** Weak OS-level privilege operations
- **GraphQL:** Overkill for MVP; REST sufficient
- **PostgreSQL:** External dependency; SQLite sufficient

## Component Diagram (Text)

┌─────────────────────────────────────────────────────────┐
│ Web UI (React) │
│ ┌──────────┬──────────────┬────────────────────────┐ │
│ │ SearchBar│ WorkspaceView│ ModeIndicator │ │
│ └──────────┴──────────────┴────────────────────────┘ │
└────────────────────────┬────────────────────────────────┘
│ REST API (JSON/HTTPS)
┌────────────────┴─────────────────┐
│ │
┌───────▼────────────────────────────────┐ │
│ Primary Device: Lia Daemon (Python) │ │
│ ┌──────────────────────────────────┐ │ │
│ │ Device Registry │ │ │
│ │ Workspace Orchestrator │ │ │
│ │ Mode Controllers │ │ │
│ │ Research Mode (whitelist) │ │ │
│ │ Concentration Mode │ │ │
│ │ AI Developer Mode │ │ │
│ │ Telemetry/Logging │ │ │
│ └──────────────────────────────────┘ │ │
│ Storage: SQLite │ │
└───────────────────────────────────────┬┘ │
│ mTLS │
┌───────────────┘ └──────────────┐
│ │
┌───────▼──────────────────────┐ ┌──────────────▼────────────────┐
│ Secondary Device 1: Agent │ │ Secondary Device N: Agent │
│ ┌──────────────────────────┐ │ │ ┌──────────────────────────┐ │
│ │ Daemon Connection │ │ │ │ Daemon Connection │ │
│ │ Mode Enforcement │ │ │ │ Mode Enforcement │ │
│ │ Status Reporting │ │ │ │ Status Reporting │ │
│ └──────────────────────────┘ │ │ └──────────────────────────┘ │
└──────────────────────────────┘ └──────────────────────────────┘

## Communication Flows

### Device Registration (Primary)

UI → Daemon: POST /api/devices/register {device_name, os}
Daemon: Generate UUID, create mTLS certificate
Daemon → UI: {device_id, certificate_pem, connection_file}

### Secondary Device Bootstrap

User: Download connection_file from primary UI
Secondary: Run agent with connection_file
Agent → Daemon: POST /api/devices/join {connection_file, device_info}
Daemon: Verify connection_file signature, register secondary
Daemon ↔ Agent: Establish mTLS connection

### Mode Activation (e.g., Concentration)

UI → Daemon: POST /api/workspaces/{id}/modes/activate {mode: "concentration", config}
Daemon: Store mode state, notify all agents
Daemon → Agents: WebSocket: {"mode": "concentration", "rules": {...}}
Agents: Enforce restrictions locally (block sites, lock apps)

## Data Models

### Device
```python
class Device:
    id: UUID
    name: str
    os: str  # "linux", "macos", "windows", etc.
    role: str  # "primary", "secondary"
    status: str  # "online", "offline"
    last_heartbeat: datetime
    certificate_thumbprint: str
    cluster_id: UUID
```

### Workspace
```python
class Workspace:
    id: UUID
    name: str
    task: str  # User's task description
    active_modes: List[str]  # ["research", "concentration"]
    active_devices: List[UUID]
    state: Dict  # Mode-specific state
    created_at: datetime
    last_active: datetime
```

### Mode Configuration
```python
class ConcentrationModeConfig:
    enabled: bool
    blocked_domains: List[str]
    blocked_apps: List[str]
    session_timer: int  # seconds
    break_glass_enabled: bool
    affected_devices: List[UUID]  # empty = primary only
```

## Security Model

- **Authentication:** mTLS certificates (daemon ↔ agent)
- **Authorization:** Role-based (primary device full control; secondary device respects directives)
- **Secrets:** Environment variables only; no hard-coded credentials
- **Privilege:** Daemon runs as system service (systemd/launchd); agents run as user service
- **Audit:** All mode activations, device connections, and policy changes logged to SQLite

See docs/SECURITY.md for threat model and mitigations.

## Cross-Platform Considerations

| Platform | Daemon Support | Agent Support | Special Notes |
|----------|----------------|---------------|---------------|
| Linux | ✅ Full | ✅ Full | Most flexible; direct system API access |
| macOS | ✅ Full | ✅ Full | Uses launchd for service; requires macOS 12+ |
| Windows | ✅ Full | ✅ Full (Phase 2) | Uses NSSM or WinSW; UI via Electron Phase 2 |
| iOS | ❌ Phase 2+ | ❌ Phase 3+ | Requires special framework; not in MVP scope |
| Android | ❌ Phase 2+ | ❌ Phase 3+ | Requires special framework; not in MVP scope |

## Extensibility Path

### Phase 1: Whitelist-based research; primary-device-only restrictions
### Phase 2: Optional AI bias evaluation (with caveats); cross-device locking
### Phase 3: Performance optimization; bare-metal hypervisor experimentation
### Phase 4: Mobile native apps; advanced AI automation

See PLANNING.md for detailed phase breakdown.
