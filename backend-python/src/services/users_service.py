from src.domain.repositories.account_repository import AccountRepository


class UsersService:
    def __init__(self, accounts: AccountRepository):
        self._accounts = accounts

    def list_accounts(self) -> list[dict]:
        accounts = self._accounts.list_accounts()

        return [
            {
                "id": account.id,
                "email": account.email,
                "role": account.role.value,
                "isActive": account.is_active,
            }
            for account in accounts
        ]