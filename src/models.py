from dataclasses import dataclass
from typing import List


@dataclass
class ARC69Attribute:
    trait_type: str
    value: str


@dataclass
class ARC69Record:
    standard: str
    external_url: str
    attributes: List[ARC69Attribute]


@dataclass
class AWENotePrefix:
    prefix: str
    receiver: str
    asset_id: int
    influence_deposit: int
    note_id: str


@dataclass
class StorageProcessedNote:
    block: int
    acfg_txn: str
    id: str
    deposit: int
    influence: int
    asset_id: str
    asset_name: str
    sender_address: str


@dataclass
class StorageMetadata:
    last_processed_block: int


@dataclass
class AlgoWorldAsset:
    index: int
    name: str
    url: str


@dataclass
class AlgoWorldCityAsset(AlgoWorldAsset):
    influence: int
    status: str
