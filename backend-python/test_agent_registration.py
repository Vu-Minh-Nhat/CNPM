
import getpass
import hashlib
import os
import sys
from pathlib import Path

import requests


# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "https://localhost:5002"

# Certificate v2
CERT_DIR = Path("../agent/certs-v2")

CLIENT_CERT = CERT_DIR / "agent.crt"
CLIENT_KEY = CERT_DIR / "agent.key"
CA_CERT = CERT_DIR / "ca.crt"

AGENT_NAME = "agent-dev-01"

# Node ID hiện có trong database arimms_python_check
NODE_ID = os.getenv("ARIMMS_TEST_NODE_ID", "").strip()

TIMEOUT = 10


# ============================================================
# CERTIFICATE UTILITIES
# ============================================================

def validate_certificate_files():
    if not NODE_ID:
        raise RuntimeError(
            "Set ARIMMS_TEST_NODE_ID to an existing Node UUID."
        )

    required_files = [
        CLIENT_CERT,
        CLIENT_KEY,
        CA_CERT,
    ]

    missing_files = [
        str(path)
        for path in required_files
        if not path.is_file()
    ]

    if missing_files:
        raise FileNotFoundError(
            "Missing certificate files:\n"
            + "\n".join(missing_files)
        )


def calculate_agent_fingerprint():
    """
    Calculate SHA-256 fingerprint from the DER-encoded
    Agent certificate.
    """
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes

    certificate = x509.load_pem_x509_certificate(
        CLIENT_CERT.read_bytes()
    )

    return certificate.fingerprint(
        hashes.SHA256()
    ).hex()


# ============================================================
# HTTP SESSION WITH MUTUAL TLS
# ============================================================

def create_mtls_session():
    session = requests.Session()

    # Client certificate authentication
    session.cert = (
        str(CLIENT_CERT),
        str(CLIENT_KEY),
    )

    # Verify Backend certificate using the new CA
    session.verify = str(CA_CERT)

    session.headers.update({
        "Content-Type": "application/json",
        "Accept": "application/json",
    })

    return session


# ============================================================
# HTTP RESPONSE UTILITIES
# ============================================================

def redact_sensitive_data(value):
    sensitive_keys = {
        "access_token",
        "accesstoken",
        "refresh_token",
        "refreshtoken",
        "token",
        "password",
        "secret",
        "authorization",
        "private_key",
    }

    if isinstance(value, dict):
        return {
            key: (
                "[REDACTED]"
                if str(key).lower() in sensitive_keys
                else redact_sensitive_data(item)
            )
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [redact_sensitive_data(item) for item in value]

    return value


def print_response(response):
    print("HTTP Status:", response.status_code)

    try:
        data = response.json()
        print("Response:", redact_sensitive_data(data))
        return data
    except ValueError:
        print("Response: [non-JSON response omitted]")
        return {}


def get_error_message(response):
    try:
        data = response.json()

        if isinstance(data, dict):
            return (
                data.get("message")
                or data.get("error")
                or str(data)
            )

        return str(data)

    except ValueError:
        return response.text


# ============================================================
# STEP 1: LOGIN
# ============================================================

def login(session):
    print("\n========== STEP 1: ADMIN LOGIN ==========")

    email = input("Administrator email: ").strip()
    password = getpass.getpass("Administrator password: ")

    if not email or not password:
        print("[ERROR] Email and password are required.")
        return None

    try:
        response = session.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": email,
                "password": password,
            },
            timeout=TIMEOUT,
        )

    except requests.exceptions.SSLError as error:
        print("[TLS ERROR] Certificate verification failed.")
        print(error)
        return None

    except requests.exceptions.RequestException as error:
        print("[CONNECTION ERROR]", error)
        return None

    data = print_response(response)

    if response.status_code != 200:
        print("[ERROR] Login failed:", get_error_message(response))
        return None

    if not isinstance(data, dict):
        print("[ERROR] Unexpected login response.")
        return None

    token = (
        data.get("access_token")
        or data.get("accessToken")
        or data.get("token")
    )

    if not token:
        print("[ERROR] JWT token not found in login response.")
        print("Please check the response field names.")
        return None

    session.headers.update({
        "Authorization": f"Bearer {token}",
    })

    print("[SUCCESS] Administrator login successful.")

    # Never print or log the JWT token.
    return token


# ============================================================
# STEP 2: REGISTER AGENT
# ============================================================

def find_agent_by_fingerprint(session, fingerprint):
    response = session.get(
        f"{BASE_URL}/agents",
        timeout=TIMEOUT,
    )

    if response.status_code != 200:
        print(
            "[ERROR] Cannot retrieve Agent list:",
            get_error_message(response),
        )
        return None

    try:
        data = response.json()
    except ValueError:
        print("[ERROR] Invalid Agent list response.")
        return None

    # Support either a direct list or a wrapped list.
    if isinstance(data, dict):
        agents = (
            data.get("agents")
            or data.get("data")
            or []
        )
    elif isinstance(data, list):
        agents = data
    else:
        agents = []

    for agent in agents:
        if not isinstance(agent, dict):
            continue

        if (
            agent.get("certificate_fingerprint", "").lower()
            == fingerprint.lower()
        ):
            return agent

    return None


def register_agent(session, fingerprint):
    print("\n========== STEP 2: REGISTER AGENT ==========")

    payload = {
        "name": AGENT_NAME,
        "certificate_fingerprint": fingerprint,
    }

    response = session.post(
        f"{BASE_URL}/agents",
        json=payload,
        timeout=TIMEOUT,
    )

    data = print_response(response)

    if response.status_code in (200, 201):
        print("[SUCCESS] Agent registered successfully.")

        if isinstance(data, dict):
            agent = (
                data.get("agent")
                or data.get("data")
                or data
            )
            return agent

        return None

    if response.status_code == 409:
        print("[INFO] Agent may already exist. Checking registry...")

        agent = find_agent_by_fingerprint(
            session,
            fingerprint,
        )

        if agent:
            print("[SUCCESS] Existing Agent found.")
            return agent

        print("[ERROR] Agent conflict, but matching fingerprint was not found.")
        return None

    print(
        "[ERROR] Agent registration failed:",
        get_error_message(response),
    )

    return None


# ============================================================
# STEP 3: ASSIGN NODE ACCESS
# ============================================================

def assign_node_access(session, agent_id):
    print("\n========== STEP 3: ASSIGN NODE ACCESS ==========")

    payload = {
        "node_id": NODE_ID,
    }

    response = session.post(
        f"{BASE_URL}/agents/{agent_id}/nodes",
        json=payload,
        timeout=TIMEOUT,
    )

    print_response(response)

    if response.status_code not in (200, 201):
        # It may already have been assigned.
        if response.status_code == 409:
            print("[INFO] Node access may already be assigned.")
            return True

        print(
            "[ERROR] Cannot assign Node:",
            get_error_message(response),
        )
        return False

    print("[SUCCESS] Node access assigned.")
    return True


# ============================================================
# STEP 4: VERIFY NODE ACCESS
# ============================================================


def verify_node_access(session, agent_id):
    print("\n========== STEP 4: VERIFY NODE ACCESS ==========")

    response = session.get(
        f"{BASE_URL}/agents/{agent_id}/nodes",
        timeout=TIMEOUT,
    )

    data = print_response(response)

    if response.status_code != 200:
        print(
            "[ERROR] Cannot verify Node access:",
            get_error_message(response),
        )
        return False

    node_ids = []

    if isinstance(data, dict):
        # Current API response format:
        # {"agent_id": "...", "node_ids": ["..."]}
        raw_node_ids = data.get("node_ids")

        if isinstance(raw_node_ids, list):
            node_ids.extend(
                str(node_id) for node_id in raw_node_ids
            )

        # Backward compatibility with other response formats.
        raw_nodes = data.get("nodes") or data.get("data") or []

        if isinstance(raw_nodes, list):
            for node in raw_nodes:
                if isinstance(node, dict):
                    node_id = node.get("node_id") or node.get("id")
                    if node_id:
                        node_ids.append(str(node_id))
                elif isinstance(node, str):
                    node_ids.append(node)

    elif isinstance(data, list):
        for node in data:
            if isinstance(node, dict):
                node_id = node.get("node_id") or node.get("id")
                if node_id:
                    node_ids.append(str(node_id))
            elif isinstance(node, str):
                node_ids.append(node)

    if NODE_ID in node_ids:
        print("[SUCCESS] Agent is authorized for the configured Node.")
        return True

    print("[ERROR] Configured Node was not found in Agent access list.")
    print("Expected Node ID:", NODE_ID)
    print("Actual Node IDs:", node_ids)
    return False



# ============================================================
# MAIN
# ============================================================

def main():
    print("==========================================")
    print(" AR-IMMS AGENT REGISTRATION TEST")
    print(" Mutual TLS + Agent Registry")
    print("==========================================")

    try:
        validate_certificate_files()

        fingerprint = calculate_agent_fingerprint()

        print("\nAgent name:", AGENT_NAME)
        print("Node ID:", NODE_ID)
        print("Certificate fingerprint:", fingerprint)

        session = create_mtls_session()

        # Step 1: Login
        token = login(session)

        if not token:
            return 1

        # Step 2: Register Agent
        agent = register_agent(
            session,
            fingerprint,
        )

        if not agent:
            return 1

        agent_id = agent.get("id") if isinstance(agent, dict) else None

        if not agent_id:
            print("[ERROR] Agent ID not found in API response.")
            print("Check the response structure of POST /agents.")
            return 1

        print("Agent ID:", agent_id)

        # Step 3: Assign Node
        if not assign_node_access(session, agent_id):
            return 1

        # Step 4: Verify Node access
        if not verify_node_access(session, agent_id):
            return 1

        print("\n==========================================")
        print("[SUCCESS] AGENT REGISTRATION TEST PASSED")
        print("==========================================")

        return 0

    except requests.exceptions.SSLError as error:
        print("\n[TLS ERROR]")
        print(error)
        print("Check Backend CA and Agent client certificate.")
        return 1

    except requests.exceptions.RequestException as error:
        print("\n[HTTP ERROR]")
        print(error)
        return 1

    except Exception as error:
        print("\n[ERROR]", error)
        return 1


if __name__ == "__main__":
    sys.exit(main())
