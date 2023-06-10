import base64
import json
import math
import time
from dataclasses import asdict
from os.path import exists
from sys import maxsize
from time import sleep

from algosdk.future.transaction import (
    AssetTransferTxn,
    LogicSig,
    LogicSigTransaction,
    PaymentTxn,
    SignedTransaction,
    Transaction,
    calculate_group_id,
)
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient

from src.shared.common import indexer
from src.shared.models import (
    AlgoWorldAsset,
    AlgoWorldCityAsset,
    ARC69Attribute,
    ARC69Record,
    AWEBuildNotePrefix,
    AWECityPackPurchaseNotePrefix,
    AWENotePrefix,
    BuildAsset,
    CityPack,
    LogicSigWallet,
    StorageMetadata,
    StorageProcessedNote,
    Wallet,
)


class Switch(dict):
    def __getitem__(self, item):
        for key in self.keys():  # iterate over the intervals
            if item in key:  # if the argument is in that interval
                return super().__getitem__(key)  # return its associated value
        raise KeyError(item)  # if not in any interval, raise KeyError


CITY_INFLUENCE_MAPPING = Switch(
    {
        range(0, 100): "AlgoWorld Regular City",
        range(100, 500): "AlgoWorld Bronze City",
        range(500, 1000): "AlgoWorld Silver City",
        range(1000, 2000): "AlgoWorld Gold City",
        range(2000, 3000): "AlgoWorld Platinum City",
        range(3000, maxsize): "AlgoWorld Diamond City",
    }
)


def pretty_print(message: str):
    print(f"\n{message}\n")


def get_city_status(influence: int):
    return CITY_INFLUENCE_MAPPING[influence]


def load(path: str):
    """
    Loads TinyBar data from a file. Returns None if file not exists.
    """
    if exists(path):
        try:
            with open(path, "r+") as f:
                return json.load(f)
        except Exception as exp:
            pretty_print(f"Unable to load {path} {exp}")
            return None
    else:
        return None


def save(path: str, data: object):
    """
    Save TinyBar data into a file.
    """
    with open(path, "w") as f:
        pretty_print(f"Saving {data}")
        json.dump(
            data,
            f,
            indent=4,
            sort_keys=True,
        )
        f.write("\n")


def load_notes(path: str):
    notes = load(path)
    if not notes:
        return {}
    else:
        return notes


def save_notes(path: str, notes: list[StorageProcessedNote]):
    return save(path, notes)


def save_aw_assets(path: str, assets: list[AlgoWorldAsset]):
    return save(path, [asdict(asset) for asset in assets])


def save_tiles_assets(path: str, assets: list[BuildAsset]):
    return save(path, [asdict(asset) for asset in assets])


def load_tiles_assets(path: str) -> list[BuildAsset]:
    tiles = [BuildAsset(**tile) for tile in load(path)]
    if not tiles:
        return []
    return tiles


def load_aw_cities(path: str) -> list[AlgoWorldCityAsset]:
    cities = [AlgoWorldCityAsset(**city) for city in load(path)]
    if not cities:
        return []
    return cities


def save_metadata(path: str, metadata: StorageMetadata):
    return save(path, asdict(metadata))


def load_packs(path: str) -> list[CityPack]:
    content = load(path)
    content = content if content else []
    packs = [CityPack(**pack) for pack in content]
    if not packs:
        return []
    return packs


def save_packs(path: str, packs: list[CityPack]):
    return save(path, [asdict(pack) for pack in packs])


def decode_note(raw_note: str):
    """
    Decodes a note into a dict.
    """
    try:
        decoded_note = base64.b64decode(raw_note).decode()

        splitted_note = decoded_note.split("_")
        note = {
            "prefix": splitted_note[0],
            "receiver": splitted_note[1],
            "asset_id": int(splitted_note[2]),
            "influence_deposit": int(splitted_note[3]),
            "note_id": splitted_note[4],
        }

        return AWENotePrefix(**note)
    except Exception as e:
        pretty_print(e)
        return None


def decode_build_note(raw_note: str):
    """
    Decodes a note into a dict.
    """
    try:
        decoded_note = base64.b64decode(raw_note).decode()

        splitted_note = decoded_note.split("_")
        note = {
            "prefix": splitted_note[0],
            "receiver": splitted_note[1],
            "asset_id": int(splitted_note[2]),
            "deposit": int(splitted_note[3]),
            "object_id": splitted_note[4],
            "note_id": splitted_note[5],
        }

        return AWEBuildNotePrefix(**note)
    except Exception as e:
        pretty_print(e)
        return None


def decode_city_pack_note(raw_note: str):
    """
    Decodes a note into a dict.
    """
    try:
        decoded_note = base64.b64decode(raw_note).decode()

        splitted_note = decoded_note.split("_")
        note = {
            "prefix": splitted_note[0],
            "operation": splitted_note[1],
            "pack_id": int(splitted_note[2]),
            "buyer_address": splitted_note[3],
        }

        return AWECityPackPurchaseNotePrefix(**note)
    except Exception as e:
        pretty_print(e)
        return None


def wait_for_confirmation(client, txid):
    """
    Utility function to wait until the transaction is
    confirmed before proceeding.
    """
    time.sleep(5)  # Sleep for 5 seconds before starting
    for attempt in range(3):  # Retry mechanism for 3 times
        try:
            last_round = client.status().get("last-round")
            txinfo = client.pending_transaction_info(txid)
            while not (
                txinfo.get("confirmed-round") and txinfo.get("confirmed-round") > 0
            ):
                pretty_print("Waiting for confirmation")
                last_round += 1
                client.status_after_block(last_round)
                txinfo = client.pending_transaction_info(txid)
            pretty_print(
                "Transaction {} confirmed in round {}.".format(
                    txid, txinfo.get("confirmed-round")
                )
            )
            return txinfo
        except Exception:
            if (
                attempt < 2
            ):  # It will try again if the number of attempts is less than 3
                pretty_print(
                    f"Attempt {attempt + 1} failed - trying again in 5 seconds."
                )
                time.sleep(5)  # Sleep for 5 seconds before retrying
            else:
                pretty_print("All attempts failed.")


def get_onchain_arc(indexer: IndexerClient, address: str, asset_index: int):
    try:
        response = indexer.search_transactions(
            address=address,
            txn_type="acfg",
            asset_id=asset_index,
        )

        if response:
            try:
                asset_config_tx = response["transactions"][0]
                arc_note = ARC69Record(
                    **json.loads(
                        base64.b64decode(asset_config_tx["note"]).decode("utf-8")
                    )
                )
                arc_note.attributes = [
                    ARC69Attribute(**attribute) for attribute in arc_note.attributes
                ]

                return arc_note

            except Exception as exp:
                pretty_print(
                    f"ARC69 not yet configured for city stats for asset index: {asset_index} {exp}"
                )
                return None
    except Exception as exp:
        pretty_print(f"Unable to fetch city stats for {address} {exp}")

    return None


def get_onchain_influence(arc_note: ARC69Record):
    if not arc_note:
        return 0

    for attribute in arc_note.attributes:
        if attribute.trait_type.lower() == "algoworld influence":
            return int(attribute.value)

    return -1


def get_onchain_city_status(arc_note: ARC69Record):
    if not arc_note:
        return None

    for attribute in arc_note.attributes:
        if attribute.trait_type.lower() == "city status":
            return attribute.value

    return None


def get_onchain_builder(arc_note: ARC69Record):
    if not arc_note:
        return None

    for attribute in arc_note.attributes:
        if attribute.trait_type.lower() == "builder":
            return attribute.value

    return None


def get_onchain_object(arc_note: ARC69Record):
    if not arc_note:
        return 0

    for attribute in arc_note.attributes:
        if attribute.trait_type.lower() == "object":
            return attribute.value

    return -1


def get_onchain_cost(arc_note: ARC69Record):
    if not arc_note:
        return 0

    for attribute in arc_note.attributes:
        if attribute.trait_type.lower() == "cost":
            return int(attribute.value)

    return -1


def filter_empty_balance_cities(
    indexer: IndexerClient, manager_address: str, all_cities: list[AlgoWorldCityAsset]
):
    all_city_ids = [city.index for city in all_cities]
    filtered_cities = []

    created_assets = indexer.search_assets(
        limit=100,
        creator=manager_address,
    )
    fetched_cities = []

    while "next-token" in created_assets:
        fetched_cities.extend(
            [asset for asset in created_assets["assets"] if asset["deleted"] is False]
        )

        created_assets = indexer.search_assets(
            limit=100, creator=manager_address, next_page=created_assets["next-token"]
        )

    for city in fetched_cities:
        city_balance = city["params"]["total"]
        if city_balance > 0 and city["index"] in all_city_ids:
            parsed_city = next(
                (x for x in all_cities if x.index == city["index"]), None
            )
            if parsed_city:
                filtered_cities.append(parsed_city)

    return filtered_cities


def get_all_tiles(
    indexer: IndexerClient,
    manager_address: str,
    all_assets: list[dict],
    all_owners: list,
):
    all_tiles = []
    index_asset = 0

    pretty_print(f"Size of all_assets {len(all_assets)}")
    pretty_print(f"Size of all_owners {len(all_owners)}")

    for asset in all_assets:
        try:
            pretty_print(
                f'Loading tile asset under {asset["index"]} and {asset["params"]["name"]}'
            )
            asset_index = asset["index"]

            cur_arc_note = get_onchain_arc(indexer, manager_address, asset_index)
            cur_builder = get_onchain_builder(cur_arc_note)
            cur_object = get_onchain_object(cur_arc_note)
            cur_cost = get_onchain_cost(cur_arc_note)

            tile = BuildAsset(
                **{
                    "index": (index_asset + 1),
                    "object": cur_object,
                    "builder": cur_builder,
                    "owner": all_owners[index_asset],
                    "cost": cur_cost,
                }
            )
            all_tiles.append(tile)
            index_asset = index_asset + 1
        except Exception as exp:
            pretty_print(f"Unable to parse asset: {asset} {exp}. Skipping...")

    return all_tiles


def get_all_cities(
    indexer: IndexerClient,
    manager_address: str,
    all_assets: list[dict],
    awc_prefix: str,
):
    all_cities = []

    for asset in all_assets:
        try:
            pretty_print(
                f'Loading potential city asset under {asset["index"]} and {asset["params"]["name"]}'
            )
            asset_index = asset["index"]

            cur_arc_note = get_onchain_arc(indexer, manager_address, asset_index)
            cur_influence = get_onchain_influence(cur_arc_note)

            if cur_influence <= 0:
                pretty_print(
                    f"Warning asset {asset_index} has influence {cur_influence}"
                )

            cur_status = get_onchain_city_status(cur_arc_note)
            cur_status = (
                get_city_status(cur_influence) if not cur_status else cur_status
            )

            city = AlgoWorldCityAsset(
                **{
                    "index": asset["index"],
                    "name": asset["params"]["name"],
                    "url": asset["params"]["url"],
                    "influence": cur_influence,
                    "status": cur_status,
                }
            )
            if (
                len(city.name) > len(awc_prefix)
                and awc_prefix == city.name[0 : len(awc_prefix)]
            ):
                all_cities.append(city)
            else:
                pretty_print(f"Skipping {city.name} - possibly not an aw city asset")
        except Exception as exp:
            pretty_print(f"Unable to parse asset: {asset} {exp}. Skipping...")

    return all_cities


def _compile_source(algod: AlgodClient, source: str):
    """Compile and return teal binary code."""
    compile_response = algod.compile(source)
    return base64.b64decode(compile_response["result"])


def logic_signature(algod: AlgodClient, teal_source: str):
    """Create and return logic signature for provided `teal_source`."""
    compiled_binary = _compile_source(algod, teal_source)
    return LogicSig(compiled_binary)


def sign(wallet, txn: Transaction) -> SignedTransaction:
    if isinstance(wallet, LogicSigWallet):
        return LogicSigTransaction(txn, wallet.logicsig)  # type: ignore

    assert wallet.private_key  # nosec
    return txn.sign(wallet.private_key)


def group_sign_send_wait(algod: AlgodClient, signers: list, txns: list[Transaction]):
    """
    Sign and send group transaction to network and wait for confirmation.
    """

    assert len(signers) == len(txns)  # nosec
    signed_group = []
    gid = calculate_group_id(txns)

    for signer, t in zip(signers, txns):
        t.group = gid
        signed_group.append(sign(signer, t))

    gtxn_id = algod.send_transactions(signed_group)
    tx_info = wait_for_confirmation(algod, txid=gtxn_id)
    return gtxn_id, tx_info


def swapper_opt_in(
    algod: AlgodClient,
    swap_creator: Wallet,
    swapper_account: LogicSigWallet,
    assets: list[int],
    funding_amount: int,
):
    params = algod.suggested_params()

    signers = [swap_creator]
    transactions = [
        PaymentTxn(
            sender=swap_creator.public_key,
            sp=params,
            receiver=swapper_account.public_key,
            amt=funding_amount,
        )
    ]

    for asset_id in assets:
        signers.append(swapper_account)
        transactions.append(
            AssetTransferTxn(
                sender=swapper_account.public_key,
                sp=params,
                receiver=swapper_account.public_key,
                amt=0,
                index=asset_id,
            )
        )

    pretty_print(f"\n --- Swapper {swapper_account.public_key} opted-in ASAs {assets}.")

    return group_sign_send_wait(algod, signers, transactions)


def sign_send_wait(algod: AlgodClient, wallet: Wallet, txn: Transaction):
    """Sign a transaction, submit it, and wait for its confirmation."""
    signed_txn = sign(wallet, txn)
    tx_id = signed_txn.transaction.get_txid()

    tx_id = algod.send_transactions([signed_txn])
    tx_info = wait_for_confirmation(algod, txid=tx_id)
    return tx_id, tx_info


def swapper_deposit(
    algod: AlgodClient,
    swap_creator: Wallet,
    swapper_account: LogicSigWallet,
    assets: dict[str, int],
):
    params = algod.suggested_params()

    deposit_txs = {}
    for asset_id, asset_amount in assets.items():
        deposit_asa_txn = AssetTransferTxn(
            sender=swap_creator.public_key,
            sp=params,
            receiver=swapper_account.public_key,
            amt=asset_amount,
            index=int(asset_id),
        )

        tx_id, _ = sign_send_wait(algod, swap_creator, deposit_asa_txn)
        sleep(5)
        deposit_txs[asset_id] = tx_id

        pretty_print(
            f"\n --- Account {swap_creator.public_key} deposited {asset_amount} "
            f"units of ASA {asset_id} into {swapper_account.public_key}."
        )

    return deposit_txs


def search_transactions_generic(
    min_round: int,
    max_round: int,
    note_prefix: str = None,
    min_amount: int = None,
    txn_type: str = None,
    limit: int = None,
    address: str = None,
    asset_id: int = None,
    chunk_size: int = 10000,
):
    if min_round > max_round:
        raise ValueError(f"min_round ({min_round}) > max_round ({max_round})")

    transactions = []
    last_min = min_round

    while True:
        try:
            # Iterate through the rounds in chunks
            for start in range(min_round, max_round + 1, chunk_size):
                end = start + chunk_size - 1
                response = indexer.search_transactions(
                    note_prefix=note_prefix,
                    min_round=start,
                    max_round=end,
                    min_amount=min_amount,
                    txn_type=txn_type,
                    limit=limit,
                    address=address,
                    asset_id=asset_id,
                )
                chunk_transactions = (
                    response["transactions"] if "transactions" in response else []
                )

                last_min = start

                if len(chunk_transactions) == 0:
                    continue
                else:
                    transactions.extend(chunk_transactions)

                print("Fetched transactions from round", start, "to", end)

            break

        except Exception as e:
            if chunk_size <= 10:
                raise e

            chunk_size = math.ceil(chunk_size // 2)  # Decrease the chunk size
            min_round = last_min
            sleep(1)  # to prevent making too many requests in a short time
            continue  # Retry with the smaller chunk size

    return transactions
