import math

from algosdk import mnemonic
from algosdk.future.transaction import AssetTransferTxn
from algosdk.v2client.indexer import IndexerClient

from src.shared.common import (
    AWT_ID,
    AWT_TOTAL_REWARDS,
    BUILD_ASSET_DB_PATH,
    BUILD_MANAGER_PASSPHRASE,
    KEYLIST_MAP,
    algod_client,
    indexer,
)
from src.shared.models import Wallet
from src.shared.utils import load_tiles_assets, pretty_print, sign_send_wait

manager_account = Wallet(
    mnemonic.to_private_key(BUILD_MANAGER_PASSPHRASE),
    mnemonic.to_public_key(BUILD_MANAGER_PASSPHRASE),
)


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


def list_builders():
    all_builders = {}

    all_tiles = load_tiles_assets(BUILD_ASSET_DB_PATH)

    for tile in all_tiles:
        if tile.builder in all_builders:
            all_builders[tile.builder][tile.object] = (
                all_builders[tile.builder][tile.object] + 1
            )
        else:
            all_builders[tile.builder] = dict.fromkeys(KEYLIST_MAP, 0)
            all_builders[tile.builder][tile.object] = 1

    return all_builders


def send_rewards(all_builders: dict, account: Wallet):
    list_account_awt = find_list_awt_accounts(indexer)
    sum_factors = 0
    validation_note = "Congratulations! You get this AWT reward thanks to your buildings on the AlgoWorld map."
    params = algod_client.suggested_params()

    for builder in all_builders:
        if all_builders[builder]["Castle"] > 0:
            all_builders[builder]["factor"] = 2
        elif all_builders[builder]["House"] > 0:
            all_builders[builder]["factor"] = 1
        else:
            all_builders[builder]["factor"] = 0
        bonus = (
            min(
                all_builders[builder]["Forest"],
                all_builders[builder]["Water"],
                all_builders[builder]["Meadow"],
            )
            * 0.2
        )
        all_builders[builder]["factor"] = all_builders[builder]["factor"] * (1 + bonus)
        sum_factors = sum_factors + all_builders[builder]["factor"]

    for builder in all_builders:
        if (all_builders[builder]["factor"] > 0) & (builder in list_account_awt):
            reward = math.floor(
                all_builders[builder]["factor"] * AWT_TOTAL_REWARDS / sum_factors
            )
            reward_txn = AssetTransferTxn(
                sender=account.public_key,
                sp=params,
                receiver=builder,
                amt=reward,
                index=AWT_ID,
                note=validation_note.encode(),
            )
            pretty_print(f"{reward} AWT sent to {builder}")
            sign_send_wait(algod_client, account, reward_txn)


def main():  # pragma: no cover
    all_builders = list_builders()
    send_rewards(all_builders, manager_account)


def init():
    if __name__ == "__main__":
        main()


init()
