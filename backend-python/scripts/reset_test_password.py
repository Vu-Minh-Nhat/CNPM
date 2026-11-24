
import getpass
from pathlib import Path
from uuid import uuid4

from dotenv import dotenv_values
from sqlalchemy import select
from sqlalchemy.engine import make_url

from src.infrastructure.databases.database import Database
from src.infrastructure.models import AccountModel, RoleModel
from src.infrastructure.security.bcrypt_password_verifier import (
    BcryptPasswordVerifier,
)

settings = dotenv_values(
    Path(__file__).resolve().parents[1] / ".env.migration"
)
database_url = settings.get("DATABASE_URL")

if (
    not database_url
    or make_url(database_url).database != "arimms_python_check"
):
    raise RuntimeError(
        "Chi duoc phep tao tai khoan trong arimms_python_check."
    )

password = getpass.getpass("Nhap mat khau test (toi thieu 8 ky tu): ")
confirmation = getpass.getpass("Nhap lai mat khau: ")

if password != confirmation:
    raise ValueError("Hai mat khau khong khop.")

if len(password) < 8 or len(password.encode("utf-8")) > 72:
    raise ValueError("Mat khau phai tu 8 ky tu va toi da 72 byte.")

password_hash = BcryptPasswordVerifier().hash_password(password)

roles = (
    ("Administrator", "System Administrator"),
    ("Operator", "System Operator"),
    ("Technician", "Technician"),
)

accounts = (
    ("admin@arimms.local", "Administrator"),
    ("operator@arimms.local", "Operator"),
    ("tech@arimms.local", "Technician"),
)

database = Database(database_url)

try:
    with database.create_session() as session:
        with session.begin():
            for code, name in roles:
                role = session.get(RoleModel, code)
                if role is None:
                    session.add(RoleModel(code=code, name=name))

            session.flush()

            for email, role_code in accounts:
                account = session.scalar(
                    select(AccountModel).filter_by(email=email)
                )

                if account is None:
                    account = AccountModel(
                        id=str(uuid4()),
                        email=email,
                        password_hash=password_hash,
                        role_code=role_code,
                        is_active=True,
                    )
                    session.add(account)
                else:
                    account.password_hash = password_hash
                    account.role_code = role_code
                    account.is_active = True

    print("Da tao/cap nhat 3 role va 3 tai khoan kiem thu.")

finally:
    database.dispose()
