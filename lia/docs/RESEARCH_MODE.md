# Research mode semantics

## Purpose

Research mode is intended for exploratory tasks where the system may need to gather external data, inspect broader contexts, or propose hypotheses without overreaching into privileged execution.

## Whitelist logic

Research mode should only permit actions that are explicitly allowed by a policy whitelist. The effective pattern is:

1. identify the requested capability
2. compare against the allowlist
3. deny by default if not present
4. log the decision and the reason for denial

In practical terms, a tool or HTTP request is valid only when:

- the target domain is included in the approved list
- the requested action falls under the allowed capability class
- the execution context is consistent with the active mode

## AI caveat framework

Research mode must surface caveats to the user before it acts beyond local context. The framework is simple:

- state the uncertainty of the source or result
- show the scope of inference
- separate observed facts from conjecture
- avoid privileged operations unless explicitly approved

This reduces the risk that research automation is mistaken for authority or certainty.
