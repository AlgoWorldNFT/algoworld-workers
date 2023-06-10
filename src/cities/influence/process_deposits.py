import string
from dataclasses import asdict
from json import dumps

from algosdk import mnemonic
from algosdk.future.transaction import AssetConfigTxn, PaymentTxn

from src.shared.common import (
    CITY_ASSET_DB_PATH,
    CITY_INFLUENCE_METADATA_PATH,
    CITY_INFLUENCE_PROCESSED_NOTES_PATH,
    LEDGER_TYPE,
    MANAGER_PASSPHRASE,
    algod_client,
    indexer,
)
from src.shared.models import (
    AlgoWorldCityAsset,
    ARC69Attribute,
    ARC69Record,
    StorageMetadata,
    StorageProcessedNote,
    Wallet,
)
from src.shared.notifications import notify_influence_deposit
from src.shared.utils import (
    decode_note,
    get_city_status,
    get_onchain_arc,
    get_onchain_influence,
    group_sign_send_wait,
    load,
    load_aw_cities,
    load_notes,
    pretty_print,
    save_metadata,
    save_notes,
    search_transactions_generic,
    sign_send_wait,
)

note = "awe_{manager_addr}_{asset_id}_{influence_deposit}_{tx_id}"
note_tr = note.encode()

awt_testnet_index = 51363057
card_index = 18725886


manager_account = Wallet(
    mnemonic.to_private_key(MANAGER_PASSPHRASE),
    mnemonic.to_public_key(MANAGER_PASSPHRASE),
)


processed_notes = load_notes(CITY_INFLUENCE_PROCESSED_NOTES_PATH)
processed_notes: dict[str, StorageProcessedNote] = (
    {} if not processed_notes else processed_notes
)
processed_note_ids = list(processed_notes.keys())

last_processed_block = load(CITY_INFLUENCE_METADATA_PATH)
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
    influence_deposit: int,
    cur_arc_note: ARC69Record,
    new_status: str,
    new_influence: int,
    deposit_txn: str = None,
):
    attributes = []

    influence_attribute = ARC69Attribute(
        trait_type="AlgoWorld influence",
        value=str(new_influence),
    )

    status_attribute = ARC69Attribute(trait_type="City status", value=new_status)
    pretty_print(f"New influence {influence_deposit} for {asset_index}")
    pretty_print(
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

    arc_update_txn = AssetConfigTxn(
        sender=account.public_key,
        sp=params,
        index=asset_index,
        manager=account.public_key,
        strict_empty_address_check=False,
        note=dumps(asdict(arc_note)),
    )

    try:
        if deposit_txn:
            validation_note = f"awe_id_{deposit_txn}"
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
            f"Unable to update city stats for receiver: {account.public_key} index: {asset_index} deposit: {influence_deposit} sender: {sender_address} {exp}"
        )

        return None


def extract_update_arc_tags(
    account: Wallet,
    sender_address: string,
    asset_index: int,
    influence_deposit: int,
    influence_deposit_txid: str,
):
    cur_arc_note, cur_influence = extract_arc_influence(
        account.public_key,
        asset_index,
    )
    new_influence = cur_influence + influence_deposit
    new_status = get_city_status(new_influence)

    return new_influence, update_arc_tags(
        account=account,
        sender_address=sender_address,
        asset_index=asset_index,
        influence_deposit=influence_deposit,
        cur_arc_note=cur_arc_note,
        new_status=new_status,
        new_influence=new_influence,
        deposit_txn=influence_deposit_txid,
    )


def extract_arc_influence(
    address: string,
    asset_index: int,
):
    cur_arc_note = get_onchain_arc(indexer, address, asset_index)
    cur_influence = get_onchain_influence(cur_arc_note)
    return cur_arc_note, cur_influence


def process_influence_txns():
    awe_prefix = f"awe_{manager_account.public_key}".encode()
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
        save_metadata(CITY_INFLUENCE_METADATA_PATH, storage_metadata)
        return

    for axfer_txn in latest_txns:
        pretty_print(axfer_txn)
        axfer_txn_note = decode_note(axfer_txn["note"])
        if axfer_txn_note:
            axfer_receiver_addr = axfer_txn["asset-transfer-transaction"]["receiver"]

            receiver_mismatch = axfer_receiver_addr != axfer_txn_note.receiver
            deposit_amount_mismatch = (
                axfer_txn_note.influence_deposit
                != axfer_txn["asset-transfer-transaction"]["amount"]
            )
            processed_deposit_txns = indexer.search_transactions(
                note_prefix=f"awe_id_{axfer_txn['id']}".encode(),
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
                    f"Skipping execution for txid: {axfer_txn['asset-transfer-transsaction']}, expected influence deposit: {axfer_txn_note.influence_deposit}, actual influence deposit: {axfer_txn}"
                )

            elif note_id_already_processed:
                pretty_print(
                    f"Skipping execution for txid: {axfer_txn['id']}, note id: {axfer_txn_note.note_id} already processed"
                )

            else:
                new_influence, tx = (
                    (
                        extract_arc_influence(
                            address=manager_account.public_key,
                            asset_index=axfer_txn_note.asset_id,
                        )[1],
                        (
                            processed_deposit_txns["transactions"][0]["id"],
                            processed_deposit_txns["transactions"][0],
                        ),
                    )
                    if transaction_already_processed
                    else extract_update_arc_tags(
                        account=manager_account,
                        sender_address=axfer_txn["sender"],
                        asset_index=axfer_txn_note.asset_id,
                        influence_deposit=axfer_txn_note.influence_deposit,
                        influence_deposit_txid=axfer_txn["id"],
                    )
                )
                confirmed_round = (
                    tx[1]["confirmed-round"] if "confirmed-round" in tx[1] else None
                )

                if confirmed_round:
                    pretty_print(
                        f'WARNING: already processed deposit of {axfer_txn_note.influence_deposit} for {axfer_txn_note.asset_id} from {axfer_txn["sender"]} at round {confirmed_round} with txid {axfer_txn["id"]}'
                    ) if transaction_already_processed else pretty_print(
                        f"successfully processed deposit of {axfer_txn_note.influence_deposit} for {axfer_txn_note.asset_id} from {axfer_txn['sender']} at round {confirmed_round}"
                    )
                    asset = indexer.asset_info(axfer_txn_note.asset_id)

                    asset_name = "N/A"

                    try:
                        asset_name = asset["asset"]["params"]["name"]
                    except Exception as exp:
                        pretty_print(f"Unable to get asset name: {exp} setting to N/A")

                    processed_notes[axfer_txn_note.note_id] = asdict(
                        StorageProcessedNote(
                            tx[1]["confirmed-round"],
                            tx[0],
                            axfer_txn_note.note_id,
                            axfer_txn_note.influence_deposit,
                            new_influence,
                            axfer_txn_note.asset_id,
                            asset_name,
                            manager_account.public_key,
                        )
                    )
                    save_notes(CITY_INFLUENCE_PROCESSED_NOTES_PATH, processed_notes)
                    storage_metadata.last_processed_block = params.first
                    save_metadata(CITY_INFLUENCE_METADATA_PATH, storage_metadata)
                    if not transaction_already_processed:
                        try:
                            notify_influence_deposit(
                                axfer_txn["sender"], new_influence, asset_name
                            )
                        except Exception as exp:
                            pretty_print(f"Unable to notify: {exp}")


def update_city_status(rogue_city: AlgoWorldCityAsset, is_capital: bool):
    cur_arc_note = get_onchain_arc(
        indexer, manager_account.public_key, rogue_city.index
    )
    new_status = (
        get_city_status(rogue_city.influence) if not is_capital else "AlgoWorld Capital"
    )
    txid, _ = update_arc_tags(
        account=manager_account,
        sender_address=manager_account.public_key,
        asset_index=rogue_city.index,
        influence_deposit=0,
        cur_arc_note=cur_arc_note,
        new_status=new_status,
        new_influence=rogue_city.influence,
        deposit_txn=None,
    )

    if txid:
        pretty_print(f"fixed rogue city status for {rogue_city.name} in {txid}")


def update_capital():
    all_cities = load_aw_cities(CITY_ASSET_DB_PATH)

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
            pretty_print(f"Skipping {first_city.name} - already capital")
    else:
        pretty_print(f"Skipping {first_city.name} - no second city")


process_influence_txns()
update_capital()
