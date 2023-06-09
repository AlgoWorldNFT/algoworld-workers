import base64

from algosdk.v2client.indexer import IndexerClient

from src.shared.common import COUNTRY_ASSET_DB_PATH, indexer
from src.shared.models import AlgoWorldAsset
from src.shared.utils import pretty_print, save_aw_assets, search_transactions_generic


def fetch_country_image_txns(
    indexer: IndexerClient,
    creator_address: str,
    asset_index: int,
):
    response = []
    max_round = 13312110 + 5000000

    note_txns = search_transactions_generic(
        address=creator_address,
        limit=100,
        min_amount=0,
        asset_id=asset_index,
        txn_type="axfer",
        max_round=max_round,
    )

    if not note_txns:
        return response

    response.extend(note_txns["transactions"])

    return [tx for tx in response if "note" in tx]


def fetch_country_image_url(
    indexer: IndexerClient, creator_address: str, asset_index: int
):
    note_txns = fetch_country_image_txns(indexer, creator_address, asset_index)
    for txn in note_txns:
        try:
            note_content = str(base64.b64decode(txn["note"]))
            if "ipfs://" in note_content:
                cid = note_content.split("\\xaf3")[0].split("ipfs://")[1]
                pretty_print(f"Found image for {asset_index} {cid}")
                return f"ipfs://{cid}"
        except Exception as exp:
            pretty_print(f"Unable to decode note for {asset_index} {exp} skipping")
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
            pretty_print(f"No image found for {asset.name} adding as is anyway")

        pretty_print(f"{asset.name} {asset.url} processed")
        all_assets_with_images.append(asset)

    return all_assets


def main():  # pragma: no cover
    creator_addresses = [
        "SXZC6IQBZNPZCOI3JR2Z7GHOHCZ2UFRH2547QDZBJ6BPIMVEJZMPZLJKWU",
        "4SP2YJCEFOGHEXJDJU73TVVG3KG4WVQC7KI55CZTGNZZL6OE52ROJ7QRLY",
    ]

    all_countries = []

    for addr in creator_addresses:
        all_countries.extend(fetch_aw_countries(indexer, addr))

    save_aw_assets(COUNTRY_ASSET_DB_PATH, all_countries)


def init():
    if __name__ == "__main__":
        main()


init()
