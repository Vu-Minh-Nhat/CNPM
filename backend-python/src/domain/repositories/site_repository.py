from abc import ABC, abstractmethod

from src.domain.models.asset import Site


class SiteRepository(ABC):
    @abstractmethod
    def list_sites(self) -> list[Site]:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, site_id: str) -> Site | None:
        raise NotImplementedError

    @abstractmethod
    def add(self, site: Site) -> Site:
        raise NotImplementedError

    @abstractmethod
    def update(
        self,
        site_id: str,
        changes: dict[str, str],
    ) -> Site | None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, site_id: str) -> bool:
        raise NotImplementedError