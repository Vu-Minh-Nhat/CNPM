from uuid import UUID, uuid4

from src.domain.exceptions import (
    ResourceNotFoundError,
    ValidationError,
)
from src.domain.models.asset import Site
from src.domain.repositories.site_repository import SiteRepository


class SitesService:
    def __init__(self, sites: SiteRepository):
        self._sites = sites

    @staticmethod
    def _validate_id(site_id: str) -> str:
        try:
            return str(UUID(site_id))
        except (ValueError, TypeError, AttributeError) as error:
            raise ValidationError("ID Site phải là UUID hợp lệ.") from error

    @staticmethod
    def _validate_payload(
        data: object,
        partial: bool = False,
    ) -> dict[str, str]:
        if not isinstance(data, dict):
            raise ValidationError("Dữ liệu phải là JSON object.")

        allowed_fields = {"code", "name"}

        if set(data) - allowed_fields:
            raise ValidationError("Dữ liệu chứa trường không được hỗ trợ.")

        if not data:
            raise ValidationError("Cần cung cấp dữ liệu.")

        if not partial and not allowed_fields.issubset(data):
            raise ValidationError("Mã và tên Site là bắt buộc.")

        result = {}

        for field, maximum in (("code", 64), ("name", 200)):
            if field not in data:
                continue

            value = data[field]

            if not isinstance(value, str) or not value.strip():
                raise ValidationError(
                    f"{field} phải là chuỗi không rỗng."
                )

            value = value.strip()

            if len(value) > maximum:
                raise ValidationError(
                    f"{field} không được vượt quá {maximum} ký tự."
                )

            result[field] = value

        return result

    def list_sites(self) -> list[Site]:
        return self._sites.list_sites()

    def get_site(self, site_id: str) -> Site:
        normalized_id = self._validate_id(site_id)
        site = self._sites.find_by_id(normalized_id)

        if site is None:
            raise ResourceNotFoundError("Không tìm thấy Site.")

        return site

    def create(self, data: object) -> Site:
        values = self._validate_payload(data)

        site = Site(
            id=str(uuid4()),
            code=values["code"],
            name=values["name"],
        )

        return self._sites.add(site)

    def update(self, site_id: str, data: object) -> Site:
        normalized_id = self._validate_id(site_id)
        values = self._validate_payload(data, partial=True)

        site = self._sites.update(normalized_id, values)

        if site is None:
            raise ResourceNotFoundError("Không tìm thấy Site.")

        return site

    def delete(self, site_id: str) -> None:
        normalized_id = self._validate_id(site_id)
        deleted = self._sites.delete(normalized_id)

        if not deleted:
            raise ResourceNotFoundError("Không tìm thấy Site.")