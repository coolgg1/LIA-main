from typing import Optional


def validate_certificate_subject(subject: Optional[str]) -> bool:
    """Minimal validation for a client certificate subject."""
    if not subject:
        return False
    return "CN=" in subject or "subjectAltName" in subject


def validate_client_credential(token: Optional[str]) -> bool:
    """Placeholder for token or mTLS credential validation."""
    if not token:
        return False
    return token.startswith("lia_") or token.startswith("cert_")
