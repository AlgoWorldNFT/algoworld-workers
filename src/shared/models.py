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
class AWEBuildNotePrefix:
    prefix: str
    receiver: str
    asset_id: int
    deposit: int
    object_id: int
    note_id: str


@dataclass
class AWECityPackPurchaseNotePrefix:
    prefix: str
    operation: str
    pack_id: int
    buyer_address: str


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
class StorageProcessedBuildNote:
    block: int
    acfg_txn: str
    id: str
    deposit: int
    object_id: int
    asset_id: str
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
class BuildAsset:
    index: int
    object: str
    builder: str
    owner: str
    cost: int


@dataclass
class AlgoWorldCityAsset(AlgoWorldAsset):
    influence: int
    status: str


@dataclass
class CityPackAsa:
    id: int
    amount: int
    decimals: int
    title: str
    url: str


@dataclass
class CityPack:
    id: int
    creator: str
    escrow: str
    contract: str
    title: str
    offered_asas: list[CityPackAsa]
    requested_algo_amount: int
    requested_algo_wallet: str
    is_active: bool
    is_closed: bool
    last_swap_tx: str


@dataclass
class LogicSigWallet:
    logicsig: str
    public_key: str


@dataclass
class Wallet:
    private_key: str
    public_key: str
