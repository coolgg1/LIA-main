# Device Bootstrap Protocol

## Connection File Format

When primary device generates a connection file for secondary devices to join:

```json
{
  "cluster_id": "a1b2c3d4-e5f6-47a8-b9c0-d1e2f3a4b5c6",
  "device_name": "My Workstation",
  "connection_token": "f1e2d3c4-b5a6-47f8-e9d0-c1b2a3f4e5d6",
  "daemon_ca_cert_pem": "-----BEGIN CERTIFICATE-----\nMIIDazCCAlOgAwIBA...\n-----END CERTIFICATE-----",
  "daemon_url": "192.168.1.100:8443",
  "expires_at": "2024-01-22T10:30:45.123456Z",
  "hmac_signature": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1"
}
```

### Fields

| Field | Type | Purpose |
|-------|------|---------|
| `cluster_id` | UUID | Which cluster to join |
| `device_name` | String | Name of the primary device (for reference) |
| `connection_token` | UUID | One-time token; proves file came from cluster |
| `daemon_ca_cert_pem` | String | CA cert for verifying daemon identity |
| `daemon_url` | String | Daemon IP:port on LAN |
| `expires_at` | ISO-8601 DateTime | File validity expiry |
| `hmac_signature` | Hex String | HMAC-SHA256 signature of all other fields |

## Validation Sequence (Secondary Device)

Agent: Read connection_file.json
Agent: Check if current_time > expires_at
If expired: REJECT ("Connection file expired")

Agent: Compute HMAC-SHA256 of all fields except hmac_signature
Agent: Compare computed HMAC with file hmac_signature
If mismatch: REJECT ("Connection file corrupted or tampered")

Agent: Extract daemon_url
Agent: Attempt TLS connection to daemon_url
Agent: Verify daemon certificate is signed by daemon_ca_cert_pem
If invalid: REJECT ("Daemon certificate invalid")

Agent: Send registration request with connection_token
Agent: Daemon verifies connection_token is valid and matches cluster_id
If invalid: REJECT ("Connection token invalid or expired")

Agent: Daemon issues device certificate
Agent: Agent stores certificate locally
Agent: Connection file deleted (one-time use)
Agent: Begin heartbeat with daemon

## Security Properties

### Protection Against Tampering
- HMAC-SHA256 signature prevents modification of any field
- If connection file is altered, signature mismatch detected immediately

### Protection Against Reuse
- connection_token tracked on daemon; can only be used once
- File expires after 24 hours; cannot be reused after expiry

### Protection Against MitM
- daemon_ca_cert_pem embedded in connection file
- Agent verifies daemon certificate against provided CA cert
- Even if network traffic intercepted, attacker can't forge daemon certificate

### Protection Against Network Spoofing
- Connection file includes specific daemon_url
- Agent connects only to specified IP:port
- Rogue daemon at different IP cannot impersonate real daemon

## Delivery Methods

**MVP (user responsibility):**
1. USB drive
2. Email attachment
3. Secure messaging app
4. QR code (generate from connection file)
5. Physical transfer

**Phase 2+ (automation):**
- Bluetooth transfer
- NFC
- Cloud sync with access controls

## Connection File Lifecycle

Daemon generates → Valid 24 hours → User downloads
↓
User transfers to secondary device (USB, email, etc.)
↓
Secondary device reads and validates connection file
↓
Secondary device registers with daemon
↓
Daemon checks connection_token is valid
↓
Daemon issues device certificate
↓
Secondary device deletes connection_file.json (one-time use)
↓
Device goes online; begins heartbeat

## Error Handling

| Error | Cause | User Action |
|-------|-------|------------|
| "Connection file expired" | File older than 24 hours | Generate new connection file on primary |
| "Connection file corrupted" | File modified or damaged | Regenerate from primary |
| "Daemon connection failed" | Cannot reach daemon IP:port | Check primary is on same LAN |
| "Daemon certificate invalid" | Daemon not on same cluster | Verify connection_file from correct primary |
| "Connection token invalid" | Token already used or expired | Generate new connection file |

## Testing Connection File Flow

```bash
# On primary device
curl -X POST http://localhost:8443/api/v1/connection-file/generate \
  -H "Authorization: Bearer primary-token"

# Copy connection-file-abc123.json to secondary device

# On secondary device
python agent/client.py bootstrap /path/to/connection-file-abc123.json

# Check logs
tail -f ~/.lia/agent.log
```