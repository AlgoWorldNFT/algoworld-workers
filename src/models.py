from dataclasses import dataclass


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
    asset_id: Number
    influence_deposit: Number
    note_id: str
