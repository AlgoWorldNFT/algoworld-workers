import base64

from algosdk.v2client.indexer import IndexerClient

from models import AlgoWorldAsset
from src.common import ALL_COUNTRIES_PATH, indexer
from src.utils import save_aw_assets


def fetch_country_image_url(
    indexer: IndexerClient, creator_address: str, asset_index: int
):
    note_txns = indexer.search_transactions(
        address=creator_address,
        asset_id=asset_index,
        limit=100,
        min_amount=0,
        txn_type="axfer",
    )

    if "transactions" in note_txns:
        for txn in note_txns["transactions"]:
            if "note" in txn:
                try:
                    note_content = str(base64.b64decode(txn["note"]))
                    if "ipfs://" in note_content:
                        cid = note_content.split("\\xaf3")[0].split("ipfs://")[1]
                        return f"https://ipfs.io/ipfs/{cid}"
                except Exception as exp:
                    print(f"Unable to decode note for {asset_index} {exp} skipping")
    return None


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

    all_assets_with_images = []

    for asset in all_assets:
        image_url = fetch_country_image_url(indexer, creator_address, asset.index)

        if image_url:
            asset.url = image_url
        else:
            print(f"No image found for {asset.name} adding as is anyway")

        print(f"{asset.name} {asset.url} processed")
        all_assets_with_images.append(asset)

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
