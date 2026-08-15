# Device Registry & Identity Model

## Overview

The device registry maintains the primary record of all devices in a Lia cluster.
Each device is assigned a unique UUID, cluster membership, role (primary/secondary),
and cryptographic identity (mTLS certificate).

## Device Model

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `device_id` | UUID | Unique device identifier (generated at registration) |
| `cluster_id` | UUID | Cluster this device belongs to |
| `name` | String | Human-readable device name |
| `os_type` | String | Operating system ("linux", "macos", "windows", "ios", "android") |
| `role` | Enum | Device role: "primary" (controls cluster) or "secondary" (member) |
| `status` | Enum | Device status: "online", "offline", "unregistered" |
| `certificate_thumbprint` | String | SHA256 fingerprint of device certificate (unique) |
| `certificate_pem` | String | Full device certificate (PEM format) |
| `private_key_pem` | String | Private key (stored on primary device only) |
| `last_heartbeat` | DateTime | Timestamp of last successful heartbeat |
| `created_at` | DateTime | Device registration timestamp |
| `updated_at` | DateTime | Last update timestamp |
| `metadata` | JSON | OS-specific capabilities, device info |

### Database Schema (SQLite)

```sql
CREATE TABLE devices (
    device_id VARCHAR(36) PRIMARY KEY,
    cluster_id VARCHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    os_type VARCHAR(50) NOT NULL,
    role VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'offline',
    certificate_thumbprint VARCHAR(64) NOT NULL UNIQUE,
    certificate_pem TEXT NOT NULL,
    private_key_pem TEXT,
    last_heartbeat DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    metadata JSON,
    FOREIGN KEY (cluster_id) REFERENCES clusters (cluster_id)
);

CREATE INDEX idx_cluster_id ON devices (cluster_id);
CREATE INDEX idx_role ON devices (role);
CREATE INDEX idx_status ON devices (status);
```

## Registration Flows

### Primary Device Registration (Cluster Bootstrap)

User → UI: "Register My Workstation"
↓
UI → Daemon POST /api/v1/devices/register
{
"name": "My Workstation",
"os_type": "linux",
"role": "primary"
}
↓
Daemon: Generate UUID for device_id
Daemon: Generate UUID for cluster_id
Daemon: Generate mTLS certificate for device
Daemon: Store in SQLite registry
Daemon: Generate connection file for cluster
↓
Daemon → UI: {
"device_id": "uuid-...",
"cluster_id": "uuid-...",
"certificate_pem": "-----BEGIN CERTIFICATE-----\n...",
"private_key_pem": "-----BEGIN PRIVATE KEY-----\n...",
"connection_file_url": "https://[daemon]/api/v1/connection-file/[cluster_id]"
}
↓
UI: Store certificate + private key locally
UI: Display connection file download link
User: Download connection_file.json

### Secondary Device Registration (Join Cluster)

User: Download connection_file.json from primary
User: Transfer to secondary device (USB, email, QR code, etc.)
↓
Secondary Agent: Read connection_file.json
Secondary Agent: Validate file signature (HMAC-SHA256)
Secondary Agent: Extract daemon_url, cluster_id, ca_cert_pem
↓
Secondary Agent → Daemon POST /api/v1/devices/register
{
"name": "My Phone",
"os_type": "android",
"role": "secondary",
"connection_token": "token-from-connection-file",
"csr_pem": "-----BEGIN CERTIFICATE REQUEST-----\n..."
}
↓
Daemon: Verify connection_token is valid and not expired
Daemon: Verify cluster_id exists
Daemon: Sign CSR with CA certificate
Daemon: Create device record in registry
↓
Daemon → Secondary: {
"device_id": "uuid-...",
"certificate_pem": "-----BEGIN CERTIFICATE-----\n...",
"private_key_pem": "-----BEGIN PRIVATE KEY-----\n..."
}
↓
Secondary Agent: Store certificate + private key locally
Secondary Agent: Delete connection_file.json (one-time use)
Secondary Agent: Begin mTLS heartbeat with daemon

## Security Notes

- **Private keys on primary only:** Secondary device private keys are NEVER stored on the primary device. Each device generates its own CSR and receives a unique certificate.
- **Certificate pinning:** Agents verify daemon certificate against CA cert from connection file.
- **One-time connection files:** Each connection file is time-limited and HMAC-signed. Expired files cannot be reused.
- **No shared secrets:** No device shares credentials with any other device. All authentication is certificate-based.
- **Heartbeat verification:** Daemon validates device certificate on each heartbeat to detect device compromise.

## Cluster Lifecycle

### Create Cluster
- Primary device registers → new cluster_id generated
- Primary is only device in cluster initially

### Add Devices
- User generates connection file (valid 24 hours)
- Secondary device downloads connection file
- Secondary registers and joins cluster
- Daemon adds device to cluster_id

### Remove Device
- Primary deletes device from registry
- Device status set to "offline"
- Device can still attempt reconnect (will fail auth)
- Complete removal requires 30-day grace period (for data sync Phase 2+)

## MVP Limitations

- Cluster per primary device (1:N hierarchy)
- No multi-cluster support
- No device-to-device trust without daemon intermediary
- No offline mode (devices go offline if daemon unreachable)
- No cloud sync (Phase 2+)