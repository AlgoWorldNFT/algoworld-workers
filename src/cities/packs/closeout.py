from dataclasses import asdict

from algosdk import mnemonic

from src.shared.common import (
    CITY_INFLUENCE_METADATA_PATH,
    CITY_INFLUENCE_PROCESSED_NOTES_PATH,
    CITY_PACK_AVAILABLE_PATH,
    CITY_PACK_METADATA_PATH,
    CITY_PACK_PURCHASED_PATH,
    LEDGER_TYPE,
    MANAGER_PASSPHRASE,
    algod_client,
    indexer,
)
from src.shared.models import StorageMetadata, StorageProcessedNote
from src.shared.utils import (
    decode_city_pack_note,
    load,
    load_packs,
    save_metadata,
    save_notes,
)

operation = "pp"  # 'pp' for pack purchase
note_decoded = f"awe_{operation}_"
note_prefix = note_decoded.encode()

awt_testnet_index = 51363057
card_index = 18725886

manager_pkey = mnemonic.to_private_key(MANAGER_PASSPHRASE)
manager_address = mnemonic.to_public_key(MANAGER_PASSPHRASE)

available_packs = load_packs(CITY_PACK_AVAILABLE_PATH)
purchased_packs = load_packs(CITY_PACK_PURCHASED_PATH)

last_processed_block = load(CITY_PACK_METADATA_PATH)
storage_metadata = (
    StorageMetadata(**last_processed_block)
    if last_processed_block
    else StorageMetadata(algod_client.suggested_params().first)
)

## tmp
storage_metadata.last_processed_block = 23932070

print(
    f"last processed block for city pack closeouts {storage_metadata.last_processed_block}"
)
print(f"Running against {LEDGER_TYPE}")


params = algod_client.suggested_params()
min_pack_price = 10_000_000
latest_pack_purchase_txns = indexer.search_transactions(
    note_prefix=note_prefix,
    min_round=storage_metadata.last_processed_block,
    max_round=params.first,
    min_amount=min_pack_price - 1,
    txn_type="pay",
)

if len(latest_pack_purchase_txns["transactions"]) == 0:
    print("No new transactions to process")
    storage_metadata.last_processed_block = params.first
    save_metadata(CITY_PACK_METADATA_PATH, storage_metadata)
    exit(0)

for pack_purchase_txn in latest_pack_purchase_txns["transactions"]:
    pack_purchase_note = decode_city_pack_note(pack_purchase_txn["note"])
    if pack_purchase_note:

        sender_mismatch = pack_purchase_txn["sender"] != pack_purchase_note.buyer_addres

        pack_exists = pack_purchase_note.pack_id in [
            pack.id for pack in available_packs
        ]

        pack_purchased = pack_purchase_note.pack_id in [
            pack.id for pack in purchased_packs
        ]

        if sender_mismatch:
            print(
                f"Sender mismatch for pack purchase {pack_purchase_txn['id']} - {pack_purchase_txn['sender']} != {pack_purchase_note.buyer_addres}"
            )

        elif pack_exists:
            print(f"Pack {pack_purchase_note.pack_id} already exists, skipping")

        elif pack_purchased:
            print(f"Pack ${pack_purchase_note.pack_id} already purchased, skipping")

        else:
            new_influence, tx = extract_update_arc_tags(
                address=manager_address,
                sender_address=axfer_txn["sender"],
                address_pkey=manager_pkey,
                asset_index=axfer_txn_note.asset_id,
                influence_deposit=axfer_txn_note.influence_deposit,
            )
            confirmed_round = (
                tx[1]["confirmed-round"] if "confirmed-round" in tx[1] else None
            )

            if confirmed_round:
                print(
                    f"successfully processed deposit of {axfer_txn_note.influence_deposit} for {axfer_txn_note.asset_id} from {axfer_txn['sender']} at round {confirmed_round}"
                )
                asset = indexer.asset_info(axfer_txn_note.asset_id)

                asset_name = "N/A"

                try:
                    asset_name = asset["asset"]["params"]["name"]
                except Exception as exp:
                    print(f"Unable to get asset name: {exp} setting to N/A")

                processed_notes[axfer_txn_note.note_id] = asdict(
                    StorageProcessedNote(
                        tx[1]["confirmed-round"],
                        tx[0],
                        axfer_txn_note.note_id,
                        axfer_txn_note.influence_deposit,
                        new_influence,
                        axfer_txn_note.asset_id,
                        asset_name,
                        manager_address,
                    )
                )
                save_notes(CITY_INFLUENCE_PROCESSED_NOTES_PATH, processed_notes)
                storage_metadata.last_processed_block = params.first
                save_metadata(CITY_INFLUENCE_METADATA_PATH, storage_metadata)
