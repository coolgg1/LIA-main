# API design

## Overview

The daemon exposes a compact REST interface for health, registration, heartbeat, and task operations. The API is intentionally minimal and consistent with a local-first security model.

## Core endpoints

### GET /health

Returns the daemon status and current version metadata.

### POST /devices/register

Creates a device record and returns a UUID.

Request body:

```
{
  "name": "workstation-alpha",
  "hardware": {
    "platform": "windows",
    "arch": "x86_64"
  }
}
```

### GET /devices/{device_id}

Returns device metadata and registration status.

### POST /agents/heartbeat

Receives a heartbeat from a connected agent.

Request body:

```
{
  "agent_id": "agent-01",
  "status": "online",
  "last_seen": "2026-08-15T12:00:00Z",
  "mode": "research"
}
```

### POST /tasks

Creates a task request with a target mode and policy set.

## Data models

### Device

- `device_id: UUID`
- `name: string`
- `created_at: datetime`
- `status: enum`
- `metadata: object`

### Agent

- `agent_id: string`
- `device_id: UUID`
- `mode: string`
- `last_seen: datetime`
- `status: string`

### Task

- `task_id: UUID`
- `agent_id: string`
- `mode: string`
- `command: string | null`
- `requested_at: datetime`
- `allowed: boolean`
