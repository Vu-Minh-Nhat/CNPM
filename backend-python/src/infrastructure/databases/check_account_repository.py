from src.create_app import create_app
from src.infrastructure.repositories.account_repository import (
    SqlAlchemyAccountRepository,
)


def check_repository() -> None:
    app = create_app()
    database = app.extensions["database"]

    repository = SqlAlchemyAccountRepository(
        session_factory=database.create_session,
    )

    try:
        account = repository.find_by_email(
            " ADMIN@ARIMMS.LOCAL "
        )

        if account is None:
            raise RuntimeError("Không tìm thấy tài khoản admin đã seed.")

        print("Tìm theo email và chuẩn hóa email: OK")
        print(f"Email: {account.email}")
        print(f"Role: {account.role.value}")
        print(f"Active: {account.is_active}")

        same_account = repository.find_by_id(account.id)

        if same_account is None or same_account.id != account.id:
            raise RuntimeError("Truy vấn lại bằng ID không khớp.")

        print("Tìm theo ID: OK")

        if repository.find_by_id("invalid-id") is not None:
            raise RuntimeError("ID sai định dạng chưa được xử lý đúng.")

        print("ID sai định dạng: trả None")
    finally:
        database.dispose()


if __name__ == "__main__":
    check_repository()