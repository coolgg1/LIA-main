# Lia Development Roadmap

## Phase 0: Foundation (Weeks 1–4)

**Goal:** Establish core infrastructure, project structure, and basic device authentication.

**Milestones:**
- [x] Project initialized with documentation and tech stack
- [ ] Week 1: Project structure, development environment, Docker setup
- [ ] Week 2: Device identity system (UUID, credentials, registry)
- [ ] Week 3: Daemon core (FastAPI, device registration, auth middleware)
- [ ] Week 4: Agent core (daemon connection) + React shell

**Deliverable:** Two devices can authenticate and maintain connection.

**Non-Goals:**
- No functional modes yet
- No UI polish
- No cross-platform testing

---

## Phase 1: Core Features (Weeks 5–10)

**Goal:** Implement three core modes and search interface.

**Milestones:**
- [ ] Week 5: Search bar parser (slash syntax, intent classification)
- [ ] Week 6: Workspace system (task state, mode layering)
- [ ] Week 7–8: Research mode (whitelist-based filtering, no AI evaluation)
- [ ] Week 9: Concentration mode (website blocking, app locking, primary device only)
- [ ] Week 10: Telemetry system and action log viewer UI

**Key Decisions:**
- Research mode starts **whitelist-only** (no AI bias evaluation in MVP)
- Concentration mode starts **primary-device-only** (secondary device locking deferred to Phase 2)
- No cloud backend (LAN-based device discovery for MVP)

**Deliverable:** User can activate modes and see restrictions enforced.

**Non-Goals:**
- Cross-device enforcement
- AI-assisted evaluation
- Shared Controller API
- Mobile support

---

## Phase 2: Cross-Device & Advanced (Weeks 11–16)

**Goal:** Extend to multi-device enforcement; introduce Shared Controller and safe AI integration.

**Milestones:**
- [ ] Week 11–12: Device hierarchy; secondary device restrictions
- [ ] Week 13–14: Shared Controller API (visual logic nodes)
- [ ] Week 15: AI Developer mode (safe attachment with user approval)
- [ ] Week 16: Research mode extended (optional AI credibility check with caveats)

**Research Mode AI Caveat Framework:**
Before integrating AI bias evaluation, MVP establishes clear contract:
- AI assessment is optional (toggle, off by default)
- AI output is never authoritative; always shown with caveat
- User always sees original sources alongside AI summary
- Data minimization: send only metadata, never full content
- Audit log all AI decisions for transparency

**Deliverable:** Multi-device workspaces; Shared Controller; AI mode with safeguards.

**Non-Goals:**
- Mobile native apps
- Cloud backend
- Advanced automation (Phase 3+)

---

## Phase 3: Hardening & Distribution (Weeks 17+)

**Goal:** Production-ready MVP.

**Milestones:**
- [ ] Performance audit and optimization
- [ ] Security hardening and threat model validation
- [ ] Cross-platform testing (Windows/macOS)
- [ ] Installer creation
- [ ] Comprehensive documentation

**Deliverable:** Stable, secure, distributable Lia MVP.

---

## Phase 4+: Long-term Roadmap

### Phase 4: Hypervisor Exploration
- Evaluate bare-metal hypervisor approach
- Prototype lightweight kernel
- Research firmware-level device management

### Phase 5: Mobile Native
- iOS app (device management, mode indicators)
- Android app (same)
- Cloud backend (optional, for remote access)

### Phase 6: Advanced AI Automation
- Complex script generation
- Autonomous optimization
- AI-driven mode transitions

---

## MVP Scope Summary

### ✅ IN
- Daemon + agent model
- Single primary device managing multiple secondary devices
- Search bar with slash commands and natural language parsing
- Research mode (whitelist-based, no AI in MVP)
- Concentration mode (primary device only, website/app blocking)
- Workspace system (task-scoped mode stacking)
- Telemetry and action logging
- Basic Shared Controller (Phase 2)
- Web-based UI (React)
- Linux + macOS support

### ❌ OUT (Deferred)
- Bare-metal hypervisor (Phase 4)
- Cloud backend (optional Phase 2+)
- Mobile native apps (Phase 5)
- Cross-device file blocking (Phase 2+)
- AI bias evaluation (Phase 2, with caveats)
- Advanced automation (Phase 3+)

---

## Weekly Breakdown: Phase 0

| Week | Component | Tasks |
|------|-----------|-------|
| 1 | Project Setup | Structure, docs, Docker, CI/CD skeleton |
| 2 | Device Identity | UUID, credentials, registry schema |
| 3 | Daemon Core | FastAPI app, auth, registration |
| 4 | Agent + UI | Agent client, React shell, integration test |

---

## Known Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Python daemon privilege escalation | Start with user-level service; move to systemd/launchd in Phase 1 |
| Cross-platform OS API differences | Abstract OS operations; implement Linux first, macOS second |
| AI bias evaluation safety | Defer to Phase 2; establish caveat framework now; require approval before enabling |
| Device discovery on closed networks | LAN-based mDNS for MVP; cloud relay optional Phase 2 |

---

## Success Metrics

- **Phase 0:** Two devices authenticate and heartbeat; CI/CD pipeline green
- **Phase 1:** Modes can be activated; restrictions visible in logs; web UI functional
- **Phase 2:** Multiple devices respond to mode changes; AI mode available with warnings
- **MVP complete:** Feature parity with Phase 0–2; <5% test failure rate; docs 100% coverage

---

## Decision Log

### Decision 1: Daemon + Agent (Not Bare-Metal Hypervisor)
**Date:** [Current]
**Rationale:** MVP timeline; proven technology stack; easier hiring and testing; clear upgrade path to hypervisor Phase 4
**Trade-off:** Cannot fully control secondary devices until Phase 2+; boot-level control deferred

### Decision 2: Python + FastAPI (Not Rust/Go)
**Date:** [Current]
**Rationale:** Fast iteration, mature ecosystem, easy async HTTP, rich library support
**Trade-off:** Slight performance penalty vs. Rust; mitigation: optimize Phase 3, migrate critical paths if needed

### Decision 3: Research Mode Whitelist-Only MVP
**Date:** [Current]
**Rationale:** AI bias evaluation unverified and unsafe; whitelist foundation established; clear Phase 2 path
**Trade-off:** MVP research mode more limited; compensated by transparent source attribution

### Decision 4: No Cloud Backend MVP
**Date:** [Current]
**Rationale:** Simpler deployment, fewer dependencies; LAN sufficient for primary use case
**Trade-off:** No remote access MVP; added Phase 2+

### Decision 5: Concentration Mode Primary-Device-Only
**Date:** [Current]
**Rationale:** Cross-device locking platform-specific and complex; MVP demonstrates core concept
**Trade-off:** Secondary device restrictions deferred; security model sufficient for MVP scope
