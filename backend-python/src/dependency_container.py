from dataclasses import dataclass

from src.domain.repositories.account_repository import AccountRepository
from src.domain.repositories.asset_repository import AssetRepository
from src.domain.security.token_provider import TokenProvider

from src.infrastructure.databases.database import Database
from src.infrastructure.repositories.account_repository import (
    SqlAlchemyAccountRepository,
)
from src.infrastructure.repositories.asset_repository import (
    SqlAlchemyAssetRepository,
)
from src.infrastructure.repositories.rack_repository import (
    SqlAlchemyRackRepository,
)
from src.infrastructure.repositories.room_repository import (
    SqlAlchemyRoomRepository,
)
from src.infrastructure.repositories.server_repository import (
    SqlAlchemyServerRepository,
)
from src.infrastructure.repositories.telemetry_repository import (
    SqlAlchemyTelemetryRepository,
)
from src.infrastructure.repositories.site_repository import (
    SqlAlchemySiteRepository,
)
from src.infrastructure.security.bcrypt_password_verifier import (
    BcryptPasswordVerifier,
)
from src.infrastructure.security.jwt_token_provider import JwtTokenProvider

from src.services.assets_service import AssetsService
from src.services.auth_service import AuthService
from src.services.login_service import LoginService
from src.services.racks_service import RacksService
from src.services.rooms_service import RoomsService
from src.services.servers_service import ServersService
from src.services.telemetry_service import TelemetryService
from src.services.session_service import SessionService
from src.services.sites_service import SitesService
from src.services.users_service import UsersService


@dataclass(frozen=True)
class Container:
    accounts: AccountRepository
    assets: AssetRepository
    tokens: TokenProvider
    login_service: LoginService
    session_service: SessionService
    users_service: UsersService
    assets_service: AssetsService
    sites_service: SitesService
    rooms_service: RoomsService
    racks_service: RacksService
    servers_service: ServersService
    telemetry_service: TelemetryService


def build_container(
    database: Database,
    jwt_secret: str,
    jwt_expires_in_seconds: int,
) -> Container:
    accounts = SqlAlchemyAccountRepository(
        session_factory=database.create_session,
    )

    assets = SqlAlchemyAssetRepository(
        session_factory=database.create_session,
    )

    sites = SqlAlchemySiteRepository(
        session_factory=database.create_session,
    )

    rooms = SqlAlchemyRoomRepository(
        session_factory=database.create_session,
    )

    racks = SqlAlchemyRackRepository(
        session_factory=database.create_session,
    )

    servers = SqlAlchemyServerRepository(
        session_factory=database.create_session,
    )
    telemetry = SqlAlchemyTelemetryRepository(
        session_factory=database.create_session,
    )

    tokens = JwtTokenProvider(
        secret=jwt_secret,
        expires_in_seconds=jwt_expires_in_seconds,
    )

    auth_service = AuthService(
        account_repository=accounts,
        password_verifier=BcryptPasswordVerifier(),
    )

    return Container(
        accounts=accounts,
        assets=assets,
        tokens=tokens,
        login_service=LoginService(
            auth_service=auth_service,
            token_provider=tokens,
        ),
        session_service=SessionService(
            accounts=accounts,
            tokens=tokens,
        ),
        users_service=UsersService(
            accounts=accounts,
            password_hasher=BcryptPasswordVerifier(),
        ),
        assets_service=AssetsService(
            assets=assets,
        ),
        sites_service=SitesService(
            sites=sites,
        ),
        rooms_service=RoomsService(
            rooms=rooms,
            sites=sites,
        ),
        racks_service=RacksService(
            racks=racks,
            rooms=rooms,
        ),
        servers_service=ServersService(
            servers=servers,
            racks=racks,
        ),
        telemetry_service=TelemetryService(
            telemetry_repository=telemetry,
        ),
    )