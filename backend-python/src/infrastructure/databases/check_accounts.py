from sqlalchemy import select

from src.create_app import create_app
from src.infrastructure.models import AccountModel


def check_accounts() -> None:
    app = create_app()
    database = app.extensions["database"]

    try:
        with database.create_session() as session:
            statement = (
                select(
                    AccountModel.email,
                    AccountModel.role_code,
                    AccountModel.is_active,
                )
                .order_by(AccountModel.email)
                .limit(5)
            )

            accounts = session.execute(statement).all()

            if not accounts:
                print("Kết nối thành công nhưng chưa có tài khoản.")
                return

            for email, role, is_active in accounts:
                print(
                    f"Email: {email} | "
                    f"Role: {role} | "
                    f"Active: {is_active}"
                )
    finally:
        database.dispose()


if __name__ == "__main__":
    check_accounts()