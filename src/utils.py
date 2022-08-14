import base64
import json
from os.path import exists
from sys import maxsize

from .models import AWENotePrefix


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
        with open(path, "r") as f:
            return json.load(f)
    else:
        return None


def save(path: str, data: dict):
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
