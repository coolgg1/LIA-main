# LIA

LIA is a local-first orchestration platform for trusted AI-assisted work. The system pairs a secure daemon, lightweight agents, and a developer-focused UI to enable research, concentration, and operational control without surrendering local ownership of the machine.

## Vision

LIA brings together three principles:

- Local trust: the daemon owns the host boundary, device identity, and credential checks.
- Intent-aware automation: agent sessions operate under explicit modes and policies.
- Human-first workflows: a focused UI surfaces the current mode, workspace activity, and governance signals.

## Architecture at a glance

- `daemon/`: secure local service that owns device registration, auth, and host connectivity.
- `agent/`: client library and service hooks for heartbeat, remote control, and task orchestration.
- `ui/`: React dashboard for workspace search, mode indicators, and operational views.
- `cli/`: administrative commands for operations and troubleshooting.

## Quick start

1. Copy `.env.example` to `.env` and adjust local settings.
2. Start the local stack:
   `make up`
3. Start the UI:
   `make ui`
4. Run unit tests:
   `make test`

## Typical usage

- Run the daemon in local development with Docker Compose.
- Connect one or more agents to the daemon using the client library.
- Switch between research, concentration, and developer modes using the UI or CLI.

## Repo structure

See `ARCHITECTURE.md` and `PLANNING.md` for deeper design notes and delivery phases.
