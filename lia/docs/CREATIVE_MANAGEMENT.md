# Certificate Management & mTLS

## Overview

Lia uses mutual TLS (mTLS) to authenticate device-to-daemon communication.
Every device receives a unique certificate signed by a cluster-specific CA.

## Certificate Hierarchy

Root CA (Primary Device)
├── Daemon Certificate (Server)
├── Primary Device Certificate (Client)
├── Secondary Device 1 Certificate (Client)
├── Secondary Device 2 Certificate (Client)
└── ...

## Certificate Generation

### Root CA (Cluster Bootstrap)

When primary device registers:
1. Daemon generates self-signed root CA certificate (3650-day validity)
2. CA certificate stored in `/etc/lia/ca.crt`
3. CA private key stored in `/etc/lia/ca.key` (readable only by daemon process)
4. CA cert embedded in connection files for secondary device verification

### Device Certificates

For each device (primary or secondary):
1. Device generates 2048-bit RSA key pair
2. Device creates Certificate Signing Request (CSR)
3. Daemon receives CSR
4. Daemon signs CSR with CA key
5. Device receives certificate (365-day validity)

## Certificate Storage

### Primary Device

/etc/lia/
├── ca.crt # Cluster CA certificate (world-readable)
├── ca.key # Cluster CA private key (root-only, mode 0600)
├── daemon.crt # Daemon server certificate
├── daemon.key # Daemon private key (root-only)
├── device.crt # Primary device client certificate
└── device.key # Primary device private key (root-only)

### Secondary Device

~/.lia/
├── ca.crt # Cluster CA cert (from connection file)
├── device.crt # Device certificate (from daemon)
└── device.key # Device private key (mode 0600)

## Certificate Validation

### Server Validation (Daemon)

When agent connects:
1. Agent presents client certificate
2. Daemon verifies certificate chain (signed by known CA)
3. Daemon verifies certificate thumbprint is in device registry
4. Daemon verifies certificate hasn't expired
5. Connection accepted or rejected

### Client Validation (Agent)

When connecting to daemon:
1. Daemon presents server certificate
2. Agent verifies certificate is signed by known CA (from connection file)
3. Agent verifies certificate hostname matches daemon_url
4. Connection accepted or rejected

## Renewal

**MVP (no automatic renewal):**
- Certificates valid 365 days
- User manually re-registers device before expiry
- Expired certificate = device offline

**Phase 2+ (automatic renewal):**
- 30 days before expiry, daemon prompts device for renewal
- Device generates new CSR, daemon signs
- Device updates local certificate
- Zero downtime renewal

## Revocation

**MVP (no revocation):**
- Delete device from registry to disable
- Deleted device certificate still technically valid
- Daemon auth check fails (device not in registry)

**Phase 2+ (CRL/OCSP):**
- Maintain Certificate Revocation List (CRL)
- Agents download CRL periodically
- Check revocation before connecting

## Security Considerations

- **Key material never transmitted:** Each device generates its own key; daemon never sees private keys except during CSR signing
- **No shared secrets:** Unlike API keys, certificates are not shared between devices
- **Time-based validity:** Certificates expire; no manual revocation needed (unless compromised)
- **Thumbprint verification:** Devices verified by certificate fingerprint, not just CN matching
- **Hardware security (future):** Phase 3+ could store private keys in TPM or secure enclave

## Testing Certificates

Generate test CA and device certificates for development:

```bash
# Generate root CA
openssl genrsa -out ca.key 2048
openssl req -new -x509 -days 3650 -key ca.key -out ca.crt \
  -subj "/CN=Lia Root CA"

# Generate device CSR
openssl genrsa -out device.key 2048
openssl req -new -key device.key -out device.csr \
  -subj "/CN=test-device.lia.local"

# Sign with CA
openssl x509 -req -days 365 -in device.csr \
  -CA ca.crt -CAkey ca.key -CAcreateserial -out device.crt
```