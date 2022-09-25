from algosdk.v2client.indexer import IndexerClient

from src.shared.common import CITY_ASSET_DB_PATH, indexer
from src.shared.utils import get_all_cities, save_aw_assets


def fetch_aw_cities(indexer: IndexerClient, manager_address: str):
    created_assets = indexer.search_assets(
        limit=100,
        creator=manager_address,
    )
    all_assets = []

    while "next-token" in created_assets:
        all_assets.extend(
            [asset for asset in created_assets["assets"] if asset["deleted"] == False]
        )

        created_assets = indexer.search_assets(
            limit=100, creator=manager_address, next_page=created_assets["next-token"]
        )

    awc_prefix = "AWC #"
    all_cities = get_all_cities(indexer, manager_address, all_assets, awc_prefix)
    all_cities.sort(key=lambda x: x.influence, reverse=False)
    save_aw_assets(CITY_ASSET_DB_PATH, all_cities)


def main():  # pragma: no cover
    manager_address = "TSYD5NUVJZLYB3MDFZSAVCSXDDH3ZABDDUARUDAWTU7KVMNVHCH2NQOYWE"
    fetch_aw_cities(indexer, manager_address)


def init():
    if __name__ == "__main__":
        main()


init()
