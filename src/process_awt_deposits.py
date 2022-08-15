import string
from dataclasses import asdict
from json import dumps

from algosdk import mnemonic
from algosdk.future.transaction import AssetConfigTxn

from src.common import (
    LEDGER_TYPE,
    MANAGER_PASSPHRASE,
    METADATA_PATH,
    PROCESSED_NOTES_PATH,
    algod_client,
    indexer,
)
from src.models import (
    AlgoWorldCityAsset,
    ARC69Attribute,
    ARC69Record,
    StorageMetadata,
    StorageProcessedNote,
)
from src.utils import (
    decode_note,
    get_all_cities,
    get_city_status,
    get_onchain_arc,
    get_onchain_influence,
    load,
    load_notes,
    save_metadata,
    save_notes,
    wait_for_confirmation,
)

note = "awe_{manager_addr}_{asset_id}_{influence_deposit}_{tx_id}"
note_tr = note.encode()

awt_testnet_index = 51363057
card_index = 18725886


manager_pkey = mnemonic.to_private_key(MANAGER_PASSPHRASE)
manager_address = mnemonic.to_public_key(MANAGER_PASSPHRASE)

processed_notes = load_notes(PROCESSED_NOTES_PATH)
processed_notes: dict[str, StorageProcessedNote] = (
    {} if not processed_notes else processed_notes
)
processed_note_ids = list(processed_notes.keys())

last_processed_block = load(METADATA_PATH)
storage_metadata = (
    StorageMetadata(**last_processed_block)
    if last_processed_block
    else StorageMetadata(algod_client.suggested_params().first)
)
print(f"last processed block {storage_metadata.last_processed_block}")
print(f"Running against {LEDGER_TYPE}")


def update_arc_tags(
    address: str,
    sender_address: str,
    address_pkey: str,
    asset_index: int,
    influence_deposit: int,
    cur_arc_note: ARC69Record,
    new_status: str,
    new_influence: int,
):
    attributes = []

    influence_attribute = ARC69Attribute(
        trait_type="AlgoWorld influence",
        value=str(new_influence),
    )

    status_attribute = ARC69Attribute(trait_type="City status", value=new_status)
    print(f"New influence {influence_deposit} for {asset_index}")
    print(
        f"New status {new_status} for {asset_index} and new influence: {new_influence} with {influence_deposit} deposit"
    )

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
        note=dumps(asdict(arc_note)),
    )

    # Sign with secret key of creator
    stxn = txn.sign(address_pkey)

    try:
        txid = algod_client.send_transaction(stxn)
        tx_info = wait_for_confirmation(algod_client, txid=txid)

        return txid, tx_info
    except Exception as exp:
        print(
            f"Unable to update city stats for receiver: {address} index: {asset_index} deposit: {influence_deposit} sender: {sender_address} {exp}"
        )

        return None


def extract_update_arc_tags(
    address: string,
    sender_address: string,
    address_pkey: string,
    asset_index: int,
    influence_deposit: int,
    note_id: string,
):
    cur_arc_note = get_onchain_arc(indexer, address, asset_index)
    cur_influence = get_onchain_influence(cur_arc_note)
    new_influence = cur_influence + influence_deposit
    new_status = get_city_status(new_influence)

    return new_influence, update_arc_tags(
        address=address,
        sender_address=sender_address,
        address_pkey=address_pkey,
        asset_index=asset_index,
        influence_deposit=influence_deposit,
        cur_arc_note=cur_arc_note,
        new_status=new_status,
        new_influence=new_influence,
    )


def process_influence_txns():
    awe_prefix = f"awe_{manager_address}".encode()
    params = algod_client.suggested_params()
    latest_txns = indexer.search_transactions(
        note_prefix=awe_prefix,
        min_round=storage_metadata.last_processed_block,
        max_round=params.first,
        txn_type="axfer",
    )

    if len(latest_txns["transactions"]) == 0:
        print("No new transactions to process")
        storage_metadata.last_processed_block = params.first
        save_metadata(METADATA_PATH, storage_metadata)
        return

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
                    f"Skipping execution for txid: {axfer_txn['id']}, expected receiver: {axfer_receiver_addr}, actual receiver: {axfer_txn_note.receiver}"
                )

            elif deposit_amount_mismatch:
                print(
                    f"Skipping execution for txid: {axfer_txn['asset-transfer-transsaction']}, expected influence deposit: {axfer_txn_note.influence_deposit}, actual influence deposit: {axfer_txn}"
                )

            elif note_id_already_processed:
                print(
                    f"Skipping execution for txid: {axfer_txn['id']}, note id: {axfer_txn_note.note_id} already processed"
                )

            else:
                new_influence, tx = extract_update_arc_tags(
                    address=manager_address,
                    sender_address=axfer_txn["sender"],
                    address_pkey=manager_pkey,
                    asset_index=axfer_txn_note.asset_id,
                    influence_deposit=axfer_txn_note.influence_deposit,
                    note_id=axfer_txn_note.note_id,
                )
                confirmed_round = (
                    tx[1]["confirmed-round"] if "confirmed-round" in tx[1] else None
                )

                if confirmed_round:
                    print(
                        f"successfully processed deposit of {axfer_txn_note.influence_deposit} for {axfer_txn_note.asset_id} from {axfer_txn['sender']} at round {confirmed_round}"
                    )
                    processed_notes[axfer_txn_note.note_id] = asdict(
                        StorageProcessedNote(
                            tx[1]["confirmed-round"],
                            tx[0],
                            axfer_txn_note.note_id,
                            axfer_txn_note.influence_deposit,
                            new_influence,
                            axfer_txn_note.asset_id,
                            manager_address,
                        )
                    )
                    save_notes(PROCESSED_NOTES_PATH, processed_notes)
                    storage_metadata.last_processed_block = params.first
                    save_metadata(METADATA_PATH, storage_metadata)

                print(f"Skipping {axfer_txn}, unable to parse note field")


def update_city_status(rogue_city: AlgoWorldCityAsset, is_capital: bool):
    cur_arc_note = get_onchain_arc(indexer, manager_address, rogue_city.index)
    txid, _ = update_arc_tags(
        address=manager_address,
        sender_address=manager_address,
        address_pkey=manager_pkey,
        asset_index=rogue_city.index,
        influence_deposit=0,
        cur_arc_note=cur_arc_note,
        new_status=get_city_status(rogue_city.influence)
        if not is_capital
        else "AlgoWorld Capital",
        new_influence=rogue_city.influence,
    )

    if txid:
        print(f"fixed rogue city status for {rogue_city.name} in {txid}")


def update_capital(manager_address: str):

    created_assets = indexer.search_assets(
        limit=100,
        creator=manager_address,
    )
    all_assets = []

    while "next-token" in created_assets:
        all_assets.extend(
            [asset for asset in created_assets["assets"] if asset["deleted"] == False]
        )

        created_assets = indexer.search_assets(
            limit=100, creator=manager_address, next_page=created_assets["next-token"]
        )

    awc_prefix = "AWC #"
    all_cities = get_all_cities(indexer, manager_address, all_assets, awc_prefix)
    all_cities.sort(key=lambda x: x.influence, reverse=True)
    first_city = all_cities.pop(0)

    rogue_cities = [
        city for city in all_cities if city.status.lower() == "algoworld capital"
    ]

    for rogue_city in rogue_cities:
        if rogue_city:
            update_city_status(rogue_city, False)

    if first_city:
        if first_city.status.lower() != "algoworld capital":
            update_city_status(first_city, True)
        else:
            print(f"Skipping {first_city.name} - already capital")
    else:
        print(f"Skipping {first_city.name} - no second city")


process_influence_txns()
update_capital(manager_address)
