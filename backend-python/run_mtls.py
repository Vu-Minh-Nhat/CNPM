
import os
import ssl
from pathlib import Path

from dotenv import load_dotenv

from src.create_app import create_app


BASE_DIR = Path(__file__).resolve().parent

# Load environment used by the existing development runner.
load_dotenv(BASE_DIR / ".env.migration")

app = create_app()

cert_dir = BASE_DIR / "certs-v2"

server_cert = Path(
    os.getenv("MTLS_SERVER_CERT", str(cert_dir / "server.crt"))
)
server_key = Path(
    os.getenv("MTLS_SERVER_KEY", str(cert_dir / "server.key"))
)
client_ca = Path(
    os.getenv("MTLS_CLIENT_CA", str(cert_dir / "ca.crt"))
)

for path in (server_cert, server_key, client_ca):
    if not path.is_file():
        raise RuntimeError(
            f"Không tìm thấy file TLS cần thiết: {path}"
        )

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.minimum_version = ssl.TLSVersion.TLSv1_2
context.load_cert_chain(
    certfile=str(server_cert),
    keyfile=str(server_key),
)
context.load_verify_locations(cafile=str(client_ca))

# Reject clients without a trusted certificate.
context.verify_mode = ssl.CERT_REQUIRED

host = os.getenv("BACKEND_HOST", "127.0.0.1")
port = int(os.getenv("BACKEND_PORT", "5002"))

print("AR-IMMS Backend starting with mandatory mTLS.")
print(f"HTTPS API: https://localhost:{port}")
print(f"Health: https://localhost:{port}/health")

app.run(
    host=host,
    port=port,
    debug=False,
    use_reloader=False,
    ssl_context=context,
)
