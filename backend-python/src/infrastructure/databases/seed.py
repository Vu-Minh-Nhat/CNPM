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
    parser = argparse.ArgumentParser(description="Tạo dữ liệu mẫu AR-IMMS.")
    parser.add_argument("--env-file", default=".env")
    parser.add_argument("--expected-database", required=True)
    args = parser.parse_args()

    backend_root = Path(__file__).resolve().parents[3]
    settings = dotenv_values(backend_root / args.env_file)
    database_url = settings.get("DATABASE_URL")

    if not database_url:
        raise RuntimeError("File cấu hình chưa có DATABASE_URL.")

    url = make_url(database_url)

    if url.database != args.expected_database:
        raise RuntimeError(
            "Tên database không khớp --expected-database. Dừng seed."
        )

    print(f"Seed database: {url.database}")

    password = getpass.getpass(
        "Đặt mật khẩu chung cho các tài khoản mẫu mới: "
    )
    confirmation = getpass.getpass("Nhập lại mật khẩu: ")

    if password != confirmation:
        raise ValueError("Hai lần nhập mật khẩu không khớp.")

    if len(password) < 8 or len(password.encode("utf-8")) > 72:
        raise ValueError(
            "Mật khẩu phải từ 8 ký tự và tối đa 72 byte UTF-8."
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
                        messages.append(f"Giữ nguyên: {model.__tablename__} | {label}")
                        return row

                    row = model(**keys, **values)
                    session.add(row)
                    session.flush()

                    messages.append(f"Đã tạo: {model.__tablename__} | {label}")
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
                    raise RuntimeError(
                        "DEMO-NODE-01 đã thuộc Rack khác. Dừng seed."
                    )

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

        # Chỉ thông báo thành công sau khi transaction đã commit.
        for message in messages:
            print(message)

        print("Seed hoàn tất.")
    finally:
        database.dispose()


if __name__ == "__main__":
    seed()