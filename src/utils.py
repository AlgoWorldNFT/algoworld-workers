import base64
import json
from dataclasses import asdict
from os.path import exists
from sys import maxsize

from algosdk.v2client.indexer import IndexerClient

from .models import (
    AlgoWorldCityAsset,
    ARC69Attribute,
    ARC69Record,
    AWENotePrefix,
    StorageMetadata,
    StorageProcessedNote,
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
            print(f"Unable to load {path} {exp}")
            return None
    else:
        return None


def save(path: str, data: object):
    """
    Save TinyBar data into a file.
    """
    with open(path, "w") as f:
        print(f"Saving {data}")
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


def save_cities(path: str, cities: list[AlgoWorldCityAsset]):
    return save(path, [asdict(city) for city in cities])


def save_metadata(path: str, metadata: StorageMetadata):
    return save(path, asdict(metadata))


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
        print(e)
        return None


def wait_for_confirmation(client, txid):
    """
    Utility function to wait until the transaction is
    confirmed before proceeding.
    """
    last_round = client.status().get("last-round")
    txinfo = client.pending_transaction_info(txid)
    while not (txinfo.get("confirmed-round") and txinfo.get("confirmed-round") > 0):
        print("Waiting for confirmation")
        last_round += 1
        client.status_after_block(last_round)
        txinfo = client.pending_transaction_info(txid)
    print(
        "Transaction {} confirmed in round {}.".format(
            txid, txinfo.get("confirmed-round")
        )
    )
    return txinfo


def get_onchain_arc(indexer: IndexerClient, address: str, asset_index: int):
    try:
        response = indexer.search_transactions(
            address=address,
            txn_type="acfg",
            asset_id=asset_index,
        )

        if response and "transactions" in response and response["transactions"]:
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
                print(
                    f"ARC69 not yet configured for city stats for asset index: {asset_index} {exp}"
                )
                return None
    except Exception as exp:
        print(f"Unable to fetch city stats for {address} {exp}")

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


def get_all_cities(
    indexer: IndexerClient,
    manager_address: str,
    all_assets: list[AlgoWorldCityAsset],
    awc_prefix: str,
):
    all_cities = []

    for asset in all_assets:

        try:
            print(
                f'Loading potential city asset under {asset["index"]} and {asset["params"]["name"]}'
            )
            asset_index = asset["index"]
            cur_arc_note = get_onchain_arc(indexer, manager_address, asset_index)
            cur_influence = get_onchain_influence(cur_arc_note)

            if cur_influence <= 0:
                print(f"Skipping asset {asset_index} with influence {cur_influence}")
                continue

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
                print(f"Skipping {city.name} - possibly not an aw city asset")
        except Exception as exp:
            print(f"Unable to parse asset: {asset} {exp}. Skipping...")

    return all_cities
