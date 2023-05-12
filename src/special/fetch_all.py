from algosdk.v2client.indexer import IndexerClient

from src.shared.common import SPECIAL_CARDS_ASSET_DB_PATH, indexer
from src.shared.models import AlgoWorldAsset
from src.shared.utils import pretty_print, save_aw_assets


def fetch_aw_special_cards(indexer: IndexerClient, manager_address: str):
    created_assets = indexer.search_assets(
        limit=100,
        creator=manager_address,
    )
    all_assets = []
    all_special = []
    name_prefix = "AW "

    while "next-token" in created_assets:
        all_assets.extend(
            [asset for asset in created_assets["assets"] if asset["deleted"] == False]
        )

        created_assets = indexer.search_assets(
            limit=100, creator=manager_address, next_page=created_assets["next-token"]
        )

    for asset in all_assets:
        try:
            special_asset = AlgoWorldAsset(
                **{
                    "index": asset["index"],
                    "name": asset["params"]["name"],
                    "url": asset["params"]["url"],
                }
            )

            if (
                len(special_asset.name) > len(name_prefix)
                and name_prefix == special_asset.name[0 : len(name_prefix)]
            ):
                all_special.append(special_asset)
        except Exception as ex:
            pretty_print("Skipping. Error parsing asset: ", ex)

    all_special.sort(key=lambda x: x.index, reverse=False)
    save_aw_assets(SPECIAL_CARDS_ASSET_DB_PATH, all_special)


def main():  # pragma: no cover
    manager_address = "HNVDQHZHQ76PDA7VQ54HFFHIYNNYTHZWJSSQVKNWMIDTDPUH7ME5W6CKIE"
    fetch_aw_special_cards(indexer, manager_address)


def init():
    if __name__ == "__main__":
        main()


init()
