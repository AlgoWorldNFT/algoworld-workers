import base64
import json
import os
import string

from algosdk import mnemonic
from algosdk.future.transaction import AssetConfigTxn

from src.common import (
    CITY_STATUS_MAPPING,
    ARC69Attribute,
    ARC69Record,
    algod_client,
    indexer,
)
from src.utils import decode_note

note = "awe_{manager_addr}_{asset_id}_{influence_deposit}_{tx_id}"
note_tr = note.encode()

awt_testnet_index = 51363057
card_index = 18725886

MANAGER_PASSPHRASE = os.environ.get(
    "MANAGER_PASSPHRASE",
    "",
)

manager_pkey = mnemonic.to_private_key(MANAGER_PASSPHRASE)
manager_address = mnemonic.to_public_key(MANAGER_PASSPHRASE)


processed_note_ids = []


def get_onchain_arc(address: string, asset_index: int):
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

    return 0


def update_arc_tags(
    address: string, address_pkey: string, asset_index: int, influence_deposit: int
):
    cur_arc_note = get_onchain_arc(address, asset_index)
    cur_influence = get_onchain_influence(cur_arc_note)
    print(f"Current influence {cur_influence} for {asset_index}")

    new_influence = cur_influence + influence_deposit
    new_status = CITY_STATUS_MAPPING[new_influence]
    influence_attribute = ARC69Attribute(
        trait_type="AlgoWorld influence",
        value=str(new_influence),
    )

    status_attribute = ARC69Attribute(trait_type="City status", value=new_status)
    print(f"New influence {influence_deposit} for {asset_index}")
    print(f"New status {new_status} for {asset_index}")

    attributes = []

    if cur_arc_note:
        attributes = [
            attribute
            for attribute in cur_arc_note.attributes
            if (
                attribute.trait_type.lower() != "algoworld influence"
                and attribute.trait_type.lower() != "city status"
            )
        ]
    attributes.extend([influence_attribute, status_attribute])
    arc_note = ARC69Record(
        standard="arc69",
        external_url="https://www.algoworld.io",
        attributes=attributes,
    )

    params = algod_client.suggested_params()

    txn = AssetConfigTxn(
        sender=address,
        sp=params,
        index=asset_index,
        manager=address,
        strict_empty_address_check=False,
        note=arc_note.json(),
    )

    # Sign with secret key of creator
    stxn = txn.sign(address_pkey)
    txid = algod_client.send_transaction(stxn)

    return txid


def process_influence_txns():
    awe_prefix = f"awe_{manager_address}".encode()
    params = algod_client.suggested_params()
    latest_txns = indexer.search_transactions(
        note_prefix=awe_prefix,
        min_round=23459525,
        max_round=params.last,
        txn_type="axfer",
    )

    for axfer_txn in latest_txns["transactions"]:
        print(axfer_txn)
        axfer_txn_note = decode_note(axfer_txn["note"])
        if axfer_txn_note:

            axfer_receiver_addr = axfer_txn["asset-transfer-transaction"]["receiver"]

            receiver_mismatch = axfer_receiver_addr != axfer_txn_note.receiver
            deposit_amount_mismatch = (
                axfer_txn_note.influence_deposit
                != axfer_txn["asset-transfer-transaction"]["amount"]
            )
            note_id_already_processed = axfer_txn_note.note_id in processed_note_ids

            if receiver_mismatch:
                print(
                    f"suspicious transaction, skipping execution for txid: {axfer_txn['id']}, expected receiver: {axfer_receiver_addr}, actual receiver: {axfer_txn_note.receiver}"
                )

            elif deposit_amount_mismatch:
                print(
                    f"suspicious transaction, skipping execution for txid: {axfer_txn['asset-transfer-transsaction']}, expected influence deposit: {axfer_txn_note.influence_deposit}, actual influence deposit: {axfer_txn}"
                )

            elif note_id_already_processed:
                print(
                    f"suspicious transaction, skipping execution for txid: {axfer_txn['id']}, note id: {axfer_txn_note.txid} already processed"
                )

            else:
                update_arc_tags(
                    address=manager_address,
                    address_pkey=manager_pkey,
                    asset_index=axfer_txn_note.asset_id,
                    influence_deposit=axfer_txn_note.influence_deposit,
                )

                print(f"Skipping {axfer_txn}, unable to parse note field")


process_influence_txns()
