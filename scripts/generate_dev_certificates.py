
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from ipaddress import ip_address
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID


ROOT = Path(__file__).resolve().parents[1]

# New certificate directories: preserve the old certificates.
CA_DIR = ROOT / "scripts" / ".dev-ca-v2"
BACKEND_CERT_DIR = ROOT / "backend-python" / "certs-v2"
AGENT_CERT_DIR = ROOT / "agent" / "certs-v2"


def create_private_key():
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )


def save_private_key(key, path):
    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_bytes(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )


def save_certificate(cert, path):
    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_bytes(
        cert.public_bytes(serialization.Encoding.PEM)
    )


def create_ca():
    key = create_private_key()

    subject = issuer = x509.Name([
        x509.NameAttribute(
            NameOID.COMMON_NAME,
            "AR-IMMS Development CA",
        ),
    ])

    now = datetime.now(timezone.utc)

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=5))
        .not_valid_after(now + timedelta(days=3650))
        .add_extension(
            x509.BasicConstraints(
                ca=True,
                path_length=0,
            ),
            critical=True,
        )
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_cert_sign=True,
                crl_sign=True,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                content_commitment=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        # Subject Key Identifier for the CA.
        .add_extension(
            x509.SubjectKeyIdentifier.from_public_key(
                key.public_key()
            ),
            critical=False,
        )
        .sign(key, hashes.SHA256())
    )

    save_private_key(key, CA_DIR / "ca.key")
    save_certificate(cert, CA_DIR / "ca.crt")

    return key, cert


def issue_certificate(
    ca_key,
    ca_cert,
    common_name,
    server=False,
):
    key = create_private_key()

    subject = x509.Name([
        x509.NameAttribute(
            NameOID.COMMON_NAME,
            common_name,
        ),
    ])

    now = datetime.now(timezone.utc)

    builder = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(ca_cert.subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=5))
        .not_valid_after(now + timedelta(days=365))
        .add_extension(
            x509.BasicConstraints(
                ca=False,
                path_length=None,
            ),
            critical=True,
        )
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_encipherment=True,
                key_cert_sign=False,
                crl_sign=False,
                data_encipherment=False,
                key_agreement=False,
                content_commitment=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        # Authority Key Identifier linking certificate to the CA.
        .add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(
                ca_cert.public_key()
            ),
            critical=False,
        )
        # Subject Key Identifier for this certificate.
        .add_extension(
            x509.SubjectKeyIdentifier.from_public_key(
                key.public_key()
            ),
            critical=False,
        )
    )

    if server:
        builder = builder.add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.IPAddress(ip_address("127.0.0.1")),
            ]),
            critical=False,
        )

    builder = builder.add_extension(
        x509.ExtendedKeyUsage([
            ExtendedKeyUsageOID.SERVER_AUTH
            if server
            else ExtendedKeyUsageOID.CLIENT_AUTH
        ]),
        critical=False,
    )

    cert = builder.sign(
        private_key=ca_key,
        algorithm=hashes.SHA256(),
    )

    return key, cert


def main():
    paths = [
        CA_DIR / "ca.key",
        CA_DIR / "ca.crt",
        BACKEND_CERT_DIR / "server.crt",
        BACKEND_CERT_DIR / "server.key",
        BACKEND_CERT_DIR / "ca.crt",
        AGENT_CERT_DIR / "agent.crt",
        AGENT_CERT_DIR / "agent.key",
        AGENT_CERT_DIR / "ca.crt",
    ]

    existing = [
        path for path in paths
        if path.exists()
    ]

    if existing:
        raise RuntimeError(
            "Certificate files already exist. "
            "No files were overwritten:\n"
            + "\n".join(str(path) for path in existing)
        )

    # Create a new development CA.
    ca_key, ca_cert = create_ca()

    # Issue Backend server certificate.
    server_key, server_cert = issue_certificate(
        ca_key=ca_key,
        ca_cert=ca_cert,
        common_name="AR-IMMS Backend",
        server=True,
    )

    # Issue Agent client certificate.
    agent_key, agent_cert = issue_certificate(
        ca_key=ca_key,
        ca_cert=ca_cert,
        common_name="agent-dev-01",
        server=False,
    )

    # Save Backend files.
    save_private_key(
        server_key,
        BACKEND_CERT_DIR / "server.key",
    )

    save_certificate(
        server_cert,
        BACKEND_CERT_DIR / "server.crt",
    )

    save_certificate(
        ca_cert,
        BACKEND_CERT_DIR / "ca.crt",
    )

    # Save Agent files.
    save_private_key(
        agent_key,
        AGENT_CERT_DIR / "agent.key",
    )

    save_certificate(
        agent_cert,
        AGENT_CERT_DIR / "agent.crt",
    )

    save_certificate(
        ca_cert,
        AGENT_CERT_DIR / "ca.crt",
    )

    # Calculate SHA-256 fingerprint from DER certificate.
    fingerprint = sha256(
        agent_cert.public_bytes(
            serialization.Encoding.DER
        )
    ).hexdigest()

    print("Development certificates created successfully.")
    print("Agent ID: agent-dev-01")
    print("Agent SHA-256 fingerprint:", fingerprint)

    print("\n===== CERTIFICATE PATHS =====")
    print("CA certificate:", CA_DIR / "ca.crt")
    print("Backend certificate:", BACKEND_CERT_DIR / "server.crt")
    print("Agent certificate:", AGENT_CERT_DIR / "agent.crt")

    print("\nPrivate keys are local development files.")
    print("Never commit private keys to Git.")


if __name__ == "__main__":
    main()
