# Security model

## Threat model

LIA assumes a hostile or untrusted runtime environment where tool execution, network egress, and local file access may be influenced by external actors or user error.

Primary risks:

- credential forgery or credential reuse
- unauthorized client connection to the daemon
- unsafe execution of commands outside a defined mode boundary
- accidental exposure of workspace data to untrusted agents

## Privilege model

The daemon is the only component allowed to own machine-level identity and trust decisions. Client processes receive delegated permissions from the daemon, not direct host privileges.

This means:

- device identity is provisioned centrally
- mTLS or signed credentials are validated at the boundary
- policy checks occur before execution requests are allowed
- workspace-level writes remain subject to explicit allowlists

## Recommended controls

- enforce TLS between daemon and clients
- validate device UUIDs and certificate chains
- require explicit allowlists for research or external execution
- log privileged operations and health events
- isolate UI, agent, and daemon traffic into separate trust domains where possible
