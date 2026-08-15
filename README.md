# Lia: Unified Cross-Device Control Plane

## What is Lia?

Lia is a daemon-based operating system control plane that unifies device management, 
task-focused workspaces, and intelligent automation across PCs, phones, tablets, and 
IoT devices.

## MVP Vision (Phase 0–1, 6–10 weeks)

- Single primary device managing secondary devices
- Unified search bar for commands and natural language control
- Three specialized modes: Research (whitelist-based), Concentration (blocking), AI Developer (safe)
- Workspace system (task-specific multi-mode environments)
- Action logging and analytics
- Web-based UI

## What's NOT in MVP

- Bare-metal hypervisor (Phase 3+)
- Cloud backend (LAN-based for MVP)
- Mobile apps (web UI only)
- Cross-device file blocking (Phase 2+)
- Advanced AI automation (Phase 2+)

## Quick Start

1. `make dev` – Start daemon + agent + UI in Docker
2. Open http://localhost:3000
3. Register primary device
4. Connect secondary device via connection file

## Tech Stack

- Backend: Python 3.11 + FastAPI
- Frontend: React 18 + TypeScript
- Storage: SQLite
- Testing: pytest + Vitest
- Deployment: Docker Compose

## Project Structure

See ARCHITECTURE.md for detailed component overview.

## Contributing

See CONTRIBUTING.md (to be created).

## Roadmap

See PLANNING.md for three-phase roadmap.

## Security

See docs/SECURITY.md for threat model and mitigation.
