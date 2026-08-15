# LIA Architecture

## Overview

LIA uses a daemon-first model: a locally hosted daemon is the trust anchor for device identity, credential validation, and host-level operations. Agent processes communicate with the daemon over a constrained, authenticated channel and expose minimal capability sets to the user or orchestrator.

## Components

### Daemon

The daemon runs as a local FastAPI service and owns the following responsibilities:

- device registration and UUID lifecycle
- mutual TLS or credential verification flows
- mode-aware policy evaluation
- health and status endpoints for clients
- registry persistence and operational logging

### Agent

The agent is a lightweight client that connects to the daemon, reports heartbeat status, and carries out workload requests. It does not own the host trust boundary; it inherits policy from the daemon.

### UI

The UI is a React dashboard that displays workspace state, active mode, and security signals. It is a presentation layer rather than the control plane.

### CLI

The CLI is used for administrative actions such as register, inspect, and revoke local machine identity and manage operational tasks from the terminal.

## Tech stack decisions

- Python 3.11+ for the daemon and CLI
- FastAPI for the API surface
- Pydantic for settings and validation
- React + TypeScript for the UI layer
- Docker Compose for a local developer environment
- GitHub Actions for a CI skeleton

## Security model

The daemon is the trust anchor. Agents and UI clients are treated as secondary consumers of daemon policy. That keeps host-level privileges concentrated while preserving a clear operational boundary for automation.
