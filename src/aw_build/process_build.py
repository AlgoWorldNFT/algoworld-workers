import math
from dataclasses import asdict
from json import dumps

from algosdk import mnemonic
from algosdk.future.transaction import AssetConfigTxn, PaymentTxn

from src.shared.common import (
    BUILD_ASSET,
    BUILD_MANAGER_PASSPHRASE,
    BUILD_METADATA_PATH,
    BUILD_PROCESSED_NOTES_PATH,
    LEDGER_TYPE,
    OWNER_FEE_PC,
    algod_client,
    indexer,
)
from src.shared.models import (
    ARC69Attribute,
    ARC69Record,
    StorageMetadata,
    StorageProcessedBuildNote,
    Wallet,
)
from src.shared.utils import (
    decode_build_note,
    get_onchain_arc,
    group_sign_send_wait,
    load,
    load_notes,
    pretty_print,
    save_metadata,
    save_notes,
    search_transactions_generic,
    sign_send_wait,
)

note = "awebuild_{manager_addr}_{asset_id}_{deposit}_{object_id}_{tx_id}"
note_tr = note.encode()

manager_account = Wallet(
    mnemonic.to_private_key(BUILD_MANAGER_PASSPHRASE),
    mnemonic.to_public_key(BUILD_MANAGER_PASSPHRASE),
)

processed_notes = load_notes(BUILD_PROCESSED_NOTES_PATH)
processed_notes: dict[str, StorageProcessedBuildNote] = (
    {} if not processed_notes else processed_notes
)
processed_note_ids = list(processed_notes.keys())

last_processed_block = load(BUILD_METADATA_PATH)
storage_metadata = (
    StorageMetadata(**last_processed_block)
    if last_processed_block
    else StorageMetadata(algod_client.suggested_params().first)
)
pretty_print(f"last processed block {storage_metadata.last_processed_block}")
pretty_print(f"Running against {LEDGER_TYPE}")


def update_arc_tags(
    account: Wallet,
    sender_address: str,
    asset_index: int,
    object_id: int,
    deposit: int,
    cur_arc_note: ARC69Record,
    deposit_txn: str = None,
):
    attributes = (
        [
            attribute
            for attribute in cur_arc_note.attributes
            if attribute.trait_type.lower() not in ["object", "builder", "cost"]
        ]
        if cur_arc_note
        else []
    )

    attributes.extend(
        [
            ARC69Attribute(trait_type="Object", value=str(object_id)),
            ARC69Attribute(trait_type="Builder", value=sender_address),
            ARC69Attribute(trait_type="Cost", value=str(deposit)),
        ]
    )

    pretty_print(f"New object {object_id} for {asset_index}")
    pretty_print(f"New builder {sender_address} for {asset_index}")

    params = algod_client.suggested_params()
    arc_update_txn = AssetConfigTxn(
        sender=account.public_key,
        sp=params,
        index=BUILD_ASSET[asset_index - 1],
        manager=account.public_key,
        strict_empty_address_check=False,
        note=dumps(
            asdict(
                ARC69Record(
                    standard="arc69",
                    external_url="https://www.algoworld.io",
                    attributes=attributes,
                )
            )
        ),
    )

    try:
        if deposit_txn:
            validation_note = f"awebuild_id_{deposit_txn}"
            validation_txn = PaymentTxn(
                sender=account.public_key,
                sp=params,
                receiver=account.public_key,
                amt=0,
                note=validation_note.encode(),
            )
            return group_sign_send_wait(
                algod_client, [account, account], [validation_txn, arc_update_txn]
            )
        else:
            return sign_send_wait(algod_client, account, arc_update_txn)
    except Exception as exp:
        pretty_print(
            f"Unable to update stats for receiver: {account.public_key} index: {asset_index} object: {object_id} sender: {sender_address} {exp}"
        )

        return None


def extract_arc_build(address: str, asset_index: int):
    return get_onchain_arc(indexer, address, asset_index)


def process_build_txns():
    awe_prefix = f"awebuild_{manager_account.public_key}".encode()
    params = algod_client.suggested_params()
    latest_txns = search_transactions_generic(
        note_prefix=awe_prefix,
        min_round=storage_metadata.last_processed_block,
        max_round=params.first,
        txn_type="axfer",
    )
    if len(latest_txns) == 0:
        pretty_print("No new transactions to process")
        storage_metadata.last_processed_block = params.first
        save_metadata(BUILD_METADATA_PATH, storage_metadata)
        return

    for axfer_txn in latest_txns:
        pretty_print(axfer_txn)
        axfer_txn_note = decode_build_note(axfer_txn["note"])
        if axfer_txn_note:
            axfer_receiver_addr = axfer_txn["asset-transfer-transaction"]["receiver"]

            receiver_mismatch = axfer_receiver_addr != axfer_txn_note.receiver
            deposit_amount_mismatch = (
                math.floor(axfer_txn_note.deposit * OWNER_FEE_PC)
                != axfer_txn["asset-transfer-transaction"]["amount"]
            )

            processed_deposit_txns = indexer.search_transactions(
                note_prefix=f"awebuild_id_{axfer_txn['id']}".encode(),
                min_round=storage_metadata.last_processed_block,
                address=manager_account.public_key,
                limit=50,
                txn_type="pay",
            )

            transaction_already_processed = (
                "transactions" in processed_deposit_txns
                and len(processed_deposit_txns["transactions"]) > 0
            )

            note_id_already_processed = axfer_txn_note.note_id in processed_note_ids

            if receiver_mismatch:
                pretty_print(
                    f"Skipping execution for txid: {axfer_txn['id']}, expected receiver: {axfer_receiver_addr}, actual receiver: {axfer_txn_note.receiver}"
                )

            elif deposit_amount_mismatch:
                pretty_print(
                    f"Skipping execution for txid: {axfer_txn['asset-transfer-transaction']}, expected deposit: {math.floor(axfer_txn_note.deposit * OWNER_FEE_PC)}, actual influence deposit: {axfer_txn}"
                )

            elif note_id_already_processed:
                pretty_print(
                    f"Skipping execution for txid: {axfer_txn['id']}, note id: {axfer_txn_note.note_id} already processed"
                )

            else:
                tx = (
                    (
                        processed_deposit_txns["transactions"][0]["id"],
                        processed_deposit_txns["transactions"][0],
                    )
                    if transaction_already_processed
                    else update_arc_tags(
                        account=manager_account,
                        sender_address=axfer_txn["sender"],
                        asset_index=axfer_txn_note.asset_id,
                        object_id=axfer_txn_note.object_id,
                        deposit=axfer_txn_note.deposit,
                        cur_arc_note=get_onchain_arc(
                            indexer,
                            manager_account.public_key,
                            axfer_txn_note.asset_id,
                        ),
                        deposit_txn=axfer_txn["id"],
                    )
                )
                confirmed_round = (
                    tx[1]["confirmed-round"] if "confirmed-round" in tx[1] else None
                )

                if confirmed_round:
                    pretty_print(
                        f'WARNING: already processed deposit of {axfer_txn_note.deposit} for {axfer_txn_note.asset_id} from {axfer_txn["sender"]} at round {confirmed_round} with txid {axfer_txn["id"]}'
                    ) if transaction_already_processed else pretty_print(
                        f"successfully processed deposit of {axfer_txn_note.deposit} for {axfer_txn_note.asset_id} from {axfer_txn['sender']} at round {confirmed_round}"
                    )
                    processed_notes[axfer_txn_note.note_id] = asdict(
                        StorageProcessedBuildNote(
                            tx[1]["confirmed-round"],
                            tx[0],
                            axfer_txn_note.note_id,
                            axfer_txn_note.deposit,
                            axfer_txn_note.object_id,
                            axfer_txn_note.asset_id,
                            manager_account.public_key,
                        )
                    )
                    save_notes(BUILD_PROCESSED_NOTES_PATH, processed_notes)
                    storage_metadata.last_processed_block = params.first
                    save_metadata(BUILD_METADATA_PATH, storage_metadata)


process_build_txns()
