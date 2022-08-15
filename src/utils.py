import base64
import json
from dataclasses import asdict
from os.path import exists
from sys import maxsize

from .models import (
    AlgoWorldCityAsset,
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
        return []
    else:
        notes


def save_notes(path: str, notes: list[StorageProcessedNote]):
    return save(path, [asdict(note) for note in notes])


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
