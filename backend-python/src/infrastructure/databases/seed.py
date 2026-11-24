import argparse
import getpass
from pathlib import Path
from uuid import uuid4

from dotenv import dotenv_values
from sqlalchemy import select
from sqlalchemy.engine import make_url

from src.infrastructure.databases.database import Database
from src.infrastructure.models import (
    AccountModel,
    NodeModel,
    RackModel,
    RoleModel,
    RoomModel,
    SiteModel,
    WorkloadModel,
)
from src.infrastructure.security.bcrypt_password_verifier import (
    BcryptPasswordVerifier,
)


def seed():
    parser = argparse.ArgumentParser(description="Táº¡o dá»¯ liá»‡u máº«u AR-IMMS.")
    parser.add_argument("--env-file", default=".env")
    parser.add_argument("--expected-database", required=True)
    args = parser.parse_args()

    backend_root = Path(__file__).resolve().parents[3]
    settings = dotenv_values(backend_root / args.env_file)
    database_url = settings.get("DATABASE_URL")

    if not database_url:
        raise RuntimeError("File cáº¥u hÃ¬nh chÆ°a cÃ³ DATABASE_URL.")

    url = make_url(database_url)

    if url.database != args.expected_database:
        raise RuntimeError(
            "TÃªn database khÃ´ng khá»›p --expected-database. Dá»«ng seed."
        )

    print(f"Seed database: {url.database}")

    password = getpass.getpass(
        "Äáº·t máº­t kháº©u chung cho cÃ¡c tÃ i khoáº£n máº«u má»›i: "
    )
    confirmation = getpass.getpass("Nháº­p láº¡i máº­t kháº©u: ")

    if password != confirmation:
        raise ValueError("Hai láº§n nháº­p máº­t kháº©u khÃ´ng khá»›p.")

    if len(password) < 8 or len(password.encode("utf-8")) > 72:
        raise ValueError(
            "Máº­t kháº©u pháº£i tá»« 8 kÃ½ tá»± vÃ  tá»‘i Ä‘a 72 byte UTF-8."
        )

    password_hash = BcryptPasswordVerifier().hash_password(password)
    database = Database(database_url)
    messages = []

    try:
        with database.create_session() as session:
            with session.begin():

                def ensure(model, keys, values):
                    row = session.scalar(
                        select(model).filter_by(**keys)
                    )

                    label = ", ".join(str(value) for value in keys.values())

                    if row is not None:
                        if model is AccountModel:
                            row.password_hash = password_hash
                            row.is_active = True
                        messages.append(f"Giá»¯ nguyÃªn: {model.__tablename__} | {label}")
                        return row

                    row = model(**keys, **values)
                    session.add(row)
                    session.flush()

                    messages.append(f"ÄÃ£ táº¡o: {model.__tablename__} | {label}")
                    return row

                roles = (
                    ("Administrator", "System Administrator"),
                    ("Operator", "System Operator"),
                    ("Technician", "Technician"),
                )

                for code, name in roles:
                    ensure(
                        RoleModel,
                        {"code": code},
                        {"name": name},
                    )

                accounts = (
                    ("admin@arimms.local", "Administrator"),
                    ("operator@arimms.local", "Operator"),
                    ("tech@arimms.local", "Technician"),
                )

                for email, role in accounts:
                    ensure(
                        AccountModel,
                        {"email": email},
                        {
                            "id": str(uuid4()),
                            "password_hash": password_hash,
                            "role_code": role,
                            "is_active": True,
                        },
                    )

                site = ensure(
                    SiteModel,
                    {"code": "DEMO-SITE"},
                    {
                        "id": str(uuid4()),
                        "name": "Mini Data Center Testbed",
                    },
                )

                room = ensure(
                    RoomModel,
                    {
                        "site_id": site.id,
                        "code": "ROOM-01",
                    },
                    {
                        "id": str(uuid4()),
                        "name": "Testbed Room",
                    },
                )

                rack = ensure(
                    RackModel,
                    {
                        "room_id": room.id,
                        "code": "RACK-01",
                    },
                    {
                        "id": str(uuid4()),
                        "name": "Testbed Rack",
                        "capacity_u": 42,
                    },
                )

                node = ensure(
                    NodeModel,
                    {"code": "DEMO-NODE-01"},
                    {
                        "id": str(uuid4()),
                        "rack_id": rack.id,
                        "name": "Testbed Server",
                        "serial_number": None,
                    },
                )

                if node.rack_id != rack.id:
                    node.rack_id = rack.id
                    session.flush()
                    messages.append("Cập nhật: DEMO-NODE-01 -> RACK-01")

                ensure(
                    WorkloadModel,
                    {
                        "node_id": node.id,
                        "code": "DEMO-WORKLOAD-01",
                    },
                    {
                        "id": str(uuid4()),
                        "name": "Simulated workload",
                        "runtime_id": None,
                    },
                )

        # Chá»‰ thÃ´ng bÃ¡o thÃ nh cÃ´ng sau khi transaction Ä‘Ã£ commit.
        for message in messages:
            print(message)

        print("Seed hoÃ n táº¥t.")
    finally:
        database.dispose()


if __name__ == "__main__":
    seed()
