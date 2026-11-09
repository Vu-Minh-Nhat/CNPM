from src.domain.models.asset import Node
from src.domain.repositories.asset_repository import AssetRepository


class AssetsService:
    def __init__(self, assets: AssetRepository):
        self._assets = assets

    def list_nodes(self) -> list[Node]:
        return self._assets.list_nodes()