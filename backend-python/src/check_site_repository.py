from src.create_app import create_app
from src.domain.exceptions import ValidationError
from src.infrastructure.repositories.site_repository import (
    SqlAlchemySiteRepository,
)
from src.services.sites_service import SitesService


def check_sites() -> None:
    app = create_app()
    database = app.extensions["database"]

    service = SitesService(
        sites=SqlAlchemySiteRepository(
            session_factory=database.create_session,
        )
    )

    try:
        sites = service.list_sites()
        print(f"Số Site: {len(sites)}")

        for site in sites[:5]:
            print(f"Site: {site.code} — {site.name}")

        if sites:
            selected = service.get_site(sites[0].id)

            if selected.id != sites[0].id:
                raise RuntimeError("Chi tiết Site không khớp.")

            print("Đọc chi tiết Site: OK")

        try:
            service.create({
                "code": "   ",
                "name": "Test",
            })
        except ValidationError:
            print("Mã chỉ có khoảng trắng bị từ chối: OK")
        else:
            raise RuntimeError("Chưa từ chối mã rỗng.")

        if sites:
            try:
                service.update(
                    sites[0].id,
                    {"name": None},
                )
            except ValidationError:
                print("Cập nhật name=null bị từ chối: OK")
            else:
                raise RuntimeError("Chưa từ chối name=null.")

        print("Site Repository và Service: OK")
    finally:
        database.dispose()


if __name__ == "__main__":
    check_sites()