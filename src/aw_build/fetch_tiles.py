from algosdk.v2client.indexer import IndexerClient

from src.shared.common import AWT_ID, BUILD_ASSET, BUILD_ASSET_DB_PATH, indexer
from src.shared.utils import get_all_tiles, save_tiles_assets


def find_list_awt_accounts(indexer: IndexerClient):
    list_account_awt = []
    next_token = None

    while True:
        params = {"next": next_token} if next_token else {}
        account_info = indexer.indexer_request(
            "GET", f"/assets/{AWT_ID}/balances", params
        )

        for account in account_info["balances"]:
            list_account_awt.append(account["address"])

        if "next-token" in account_info and account_info["next-token"]:
            next_token = account_info["next-token"]
        else:
            break

    return list_account_awt


def fetch_tiles(indexer: IndexerClient, manager_address: str):
    all_assets = []
    all_owners = []

    list_account_awt = find_list_awt_accounts(indexer)

    for asset_id in BUILD_ASSET:
        created_assets = indexer.search_assets(asset_id=asset_id)
        all_assets.extend(
            asset for asset in created_assets["assets"] if not asset["deleted"]
        )

        response = indexer.asset_balances(asset_id=asset_id)
        accounts = response["balances"]

        for account in accounts:
            if account["amount"] > 0:
                address = account["address"]
                if address in list_account_awt:
                    all_owners.append(address)
                else:
                    print(f"Unable to find AWT in owner wallet {address}")
                    all_owners.append(manager_address)

    all_tiles = get_all_tiles(indexer, manager_address, all_assets, all_owners)
    save_tiles_assets(BUILD_ASSET_DB_PATH, all_tiles)


def main():  # pragma: no cover
    manager_address = "75BMV3IXUMULXWV4JCCEET3OXZQU5J32J5CZ62A4DOH4HHF3KTFFX56ZZQ"
    fetch_tiles(indexer, manager_address)


if __name__ == "__main__":
    main()
