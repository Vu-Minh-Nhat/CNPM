from dataclasses import dataclass

from src.services.telemetry_query_service import TelemetryQueryService

from src.domain.repositories.account_repository import AccountRepository
from src.domain.repositories.alert_repository import AlertRepository
from src.domain.repositories.asset_repository import AssetRepository
from src.domain.repositories.marker_repository import MarkerRepository
from src.domain.repositories.telemetry_repository import TelemetryRepository
from src.domain.repositories.ticket_history_repository import (
    TicketHistoryRepository,
)
from src.domain.repositories.ticket_repository import TicketRepository
from src.domain.security.token_provider import TokenProvider

from src.infrastructure.databases.database import Database
from src.infrastructure.repositories.account_repository import (
    SqlAlchemyAccountRepository,
)
from src.infrastructure.repositories.alert_repository import (
    SqlAlchemyAlertRepository,
)
from src.infrastructure.repositories.asset_repository import (
    SqlAlchemyAssetRepository,
)
from src.infrastructure.repositories.marker_repository import (
    SqlAlchemyMarkerRepository,
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
from src.infrastructure.repositories.site_repository import (
    SqlAlchemySiteRepository,
)
from src.infrastructure.repositories.telemetry_repository import (
    SqlAlchemyTelemetryRepository,
)
from src.infrastructure.repositories.ticket_history_repository import (
    SqlAlchemyTicketHistoryRepository,
)
from src.infrastructure.repositories.ticket_repository import (
    SqlAlchemyTicketRepository,
)
from src.infrastructure.security.bcrypt_password_verifier import (
    BcryptPasswordVerifier,
)
from src.infrastructure.security.jwt_token_provider import JwtTokenProvider

from src.services.assets_service import AssetsService
from src.services.alert_service import AlertService
from src.services.auth_service import AuthService
from src.services.login_service import LoginService
from src.services.marker_service import MarkerService
from src.services.racks_service import RacksService
from src.services.rooms_service import RoomsService
from src.services.servers_service import ServersService
from src.services.session_service import SessionService
from src.services.sites_service import SitesService
from src.services.telemetry_service import TelemetryService
from src.services.users_service import UsersService
from src.services.alert_service import AlertService

@dataclass(frozen=True)
class Container:
    accounts: AccountRepository
    assets: AssetRepository
    telemetry_repository: TelemetryRepository
    alert_repository: AlertRepository
    alert_service: AlertService
    ticket_repository: TicketRepository
    ticket_history_repository: TicketHistoryRepository
    marker_repository: MarkerRepository
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
    telemetry_query_service: TelemetryQueryService
    marker_service: MarkerService


def build_container(
    database: Database,
    jwt_secret: str,
    jwt_expires_in_seconds: int,
    stale_after_seconds: int = 30,
    offline_after_seconds: int = 90,
    poll_interval_seconds: int = 5,
) -> Container:
    accounts = SqlAlchemyAccountRepository(
        session_factory=database.create_session
    )
    assets = SqlAlchemyAssetRepository(
        session_factory=database.create_session
    )
    sites = SqlAlchemySiteRepository(
        session_factory=database.create_session
    )
    rooms = SqlAlchemyRoomRepository(
        session_factory=database.create_session
    )
    racks = SqlAlchemyRackRepository(
        session_factory=database.create_session
    )
    servers = SqlAlchemyServerRepository(
        session_factory=database.create_session
    )
    telemetry_repository = SqlAlchemyTelemetryRepository(
        session_factory=database.create_session
    )
    alert_repository = SqlAlchemyAlertRepository(
        session_factory=database.create_session
    )
    ticket_repository = SqlAlchemyTicketRepository(
        session_factory=database.create_session
    )
    ticket_history_repository = SqlAlchemyTicketHistoryRepository(
        session_factory=database.create_session
    )
    marker_repository = SqlAlchemyMarkerRepository(
        session_factory=database.create_session
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
        telemetry_repository=telemetry_repository,
        alert_repository=alert_repository,
        alert_service=AlertService(alerts=alert_repository),
        ticket_repository=ticket_repository,
        ticket_history_repository=ticket_history_repository,
        marker_repository=marker_repository,
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
        assets_service=AssetsService(assets=assets),
        sites_service=SitesService(sites=sites),
        rooms_service=RoomsService(rooms=rooms, sites=sites),
        racks_service=RacksService(racks=racks, rooms=rooms),
        servers_service=ServersService(servers=servers, racks=racks),
        telemetry_service=TelemetryService(
            telemetry_repository=telemetry_repository,
        ),
        telemetry_query_service=TelemetryQueryService(
            telemetry_repository=telemetry_repository,
            server_repository=servers,
            stale_after_seconds=stale_after_seconds,
            offline_after_seconds=offline_after_seconds,
            poll_interval_seconds=poll_interval_seconds,
        ),
        marker_service=MarkerService(
            repository=marker_repository,
            assets=assets,
        ),
    )