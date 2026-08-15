# LIA Planning

## Product goals

The project is designed to deliver an agentic system that remains transparent, secure, and operable in a local environment. Product work is staged so the foundation is reliable before more advanced workflows are added.

## Phase 1: Foundation

- Define the daemon-host contract and local trust model.
- Establish device identity and registry persistence.
- Implement minimal API surfaces and environment configuration.
- Add smoke tests for registry and device workflows.

Milestone: secure local daemon ready for local-only testing.

## Phase 2: Agent connectivity

- Build the agent client with heartbeats and reconnect semantics.
- Add health checks and operational status reporting.
- Wire UI to the daemon for workspace and mode telemetry.

Milestone: a single agent can connect and report status reliably.

## Phase 3: Mode-driven workflows

- Implement research, concentration, and developer mode policy boundaries.
- Enforce user-controlled allowlists and command restrictions.
- Add UI indicators and mode-specific workspace behavior.

Milestone: users can clearly distinguish and reason about the active mode.

## Phase 4: Hardening and release readiness

- Expand security review and privilege boundaries.
- Add CI validation, linting, and packaging automation.
- Prepare operational runbooks and deployment defaults.

Milestone: production-ready baseline for local and staging deployment.

## Timeline

- Weeks 1-2: daemon foundation and identity model
- Weeks 3-4: agent heartbeat and status logic
- Weeks 5-6: UI and mode policy work
- Weeks 7-8: hardening, CI, documentation
