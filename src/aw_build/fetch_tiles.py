from algosdk.v2client.indexer import IndexerClient

from src.shared.common import AWT_ID, BUILD_ASSET, BUILD_ASSET_DB_PATH, indexer
from src.shared.utils import get_all_tiles, save_tiles_assets


def find_list_awt_accounts(indexer: IndexerClient):
    list_account_awt = []

    account_info_first = indexer.indexer_request(
        "GET", "/assets/" + str(AWT_ID) + "/balances"
    )

    for account in account_info_first["balances"]:
        list_account_awt.append(account["address"])

    next_token = account_info_first["next-token"]

    flag = 0

    while flag == 0:
        account_info = indexer.indexer_request(
            "GET",
            "/assets/" + str(AWT_ID) + "/balances",
            {"next": next_token},
        )

        for account in account_info["balances"]:
            list_account_awt.append(account["address"])

        if "next-token" in account_info:
            next_token = account_info["next-token"]
        else:
            flag = 1

    return list_account_awt


def fetch_tiles(indexer: IndexerClient, manager_address: str):
    all_assets = []
    all_owners = []

    list_account_awt = find_list_awt_accounts(indexer)

    for i in range(len(BUILD_ASSET)):
        created_assets = indexer.search_assets(asset_id=BUILD_ASSET[i])
        all_assets.extend(
            [asset for asset in created_assets["assets"] if asset["deleted"] == False]
        )

        response = indexer.asset_balances(asset_id=BUILD_ASSET[i])
        accounts = response["balances"]

        for account in accounts:
            if account["amount"] > 0:
                if account["address"] in list_account_awt:
                    all_owners.append(account["address"])
                else:
                    print(f"Unable to find AWT in owner wallet {account['address']}")
                    all_owners.append(manager_address)

    all_tiles = get_all_tiles(indexer, manager_address, all_assets, all_owners)
    save_tiles_assets(BUILD_ASSET_DB_PATH, all_tiles)


def main():  # pragma: no cover
    manager_address = "75BMV3IXUMULXWV4JCCEET3OXZQU5J32J5CZ62A4DOH4HHF3KTFFX56ZZQ"
    fetch_tiles(indexer, manager_address)


def init():
    if __name__ == "__main__":
        main()


init()
