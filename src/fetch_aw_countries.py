from algosdk.v2client.indexer import IndexerClient

from models import AlgoWorldAsset
from src.common import ALL_COUNTRIES_PATH, indexer
from src.utils import save_aw_assets


def fetch_aw_countries(indexer: IndexerClient, creator_address: str):
    created_assets = indexer.search_assets(
        limit=100,
        creator=creator_address,
    )
    all_assets = []

    while "next-token" in created_assets:
        all_assets.extend(
            [
                AlgoWorldAsset(
                    asset["index"], asset["params"]["name"], asset["params"]["url"]
                )
                for asset in created_assets["assets"]
                if asset["deleted"] == False
                and "name" in asset["params"]
                and asset["params"]["name"].startswith("AW #")
            ]
        )

        created_assets = indexer.search_assets(
            limit=100, creator=creator_address, next_page=created_assets["next-token"]
        )

    return all_assets


creator_addresses = [
    "SXZC6IQBZNPZCOI3JR2Z7GHOHCZ2UFRH2547QDZBJ6BPIMVEJZMPZLJKWU",
    "4SP2YJCEFOGHEXJDJU73TVVG3KG4WVQC7KI55CZTGNZZL6OE52ROJ7QRLY",
]

all_countries = []

for addr in creator_addresses:
    all_countries.extend(fetch_aw_countries(indexer, addr))

save_aw_assets(ALL_COUNTRIES_PATH, all_countries)

# Save indexes (manual for now)
