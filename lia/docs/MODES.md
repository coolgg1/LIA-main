# Operating modes

LIA is designed to make the active operating mode visible and governable. Every mode defines allowed behavior, audience, and confidence requirements.

## Research mode

Purpose: object discovery, external search, synthesis, and comparative analysis.

- allowed: read-only analysis, whitelisted network lookups, local documentation review
- restricted: destructive commands, secret-handling, autonomous system modifications

## Concentration mode

Purpose: deeply focused work on a known task with minimal distraction and narrow execution.

- allowed: write access to the active workspace, focused code edits, predictable local execution
- restricted: broad exploratory tooling, uncontrolled automation, non-essential system side effects

## AI developer mode

Purpose: development assistance where the system supports implementation, verification, and code review under explicit policy.

- allowed: scoped code generation, tests, CI commands, and local validation
- restricted: production-like privileged operations without human approval

## Governance principle

The mode is not merely a label. It controls policy and trust boundaries. UI, daemon, and agent logic should all display the current mode and enforce the matching policy set.
