import base64
import math

from algosdk import mnemonic
from algosdk.future.transaction import AssetTransferTxn, LogicSig, PaymentTxn
from retry import retry

from src.shared.common import (
    CITY_PACK_AVAILABLE_PATH,
    CITY_PACK_METADATA_PATH,
    CITY_PACK_PURCHASED_PATH,
    LEDGER_TYPE,
    MANAGER_PASSPHRASE,
    algod_client,
    indexer,
)
from src.shared.models import CityPack, LogicSigWallet, StorageMetadata, Wallet
from src.shared.notifications import notify_citypack_purchase
from src.shared.utils import (
    decode_city_pack_note,
    group_sign_send_wait,
    load,
    load_packs,
    pretty_print,
    save_metadata,
    save_packs,
)


@retry(tries=3, delay=1, backoff=2)
def _get_transactions_between_rounds(
    note_prefix: str, min_round, max_round, min_pack_price, chunk_size
):
    print(f"Searching transactions between rounds {min_round} and {max_round}...")
    return indexer.search_transactions(
        note_prefix=note_prefix,
        min_round=min_round,
        max_round=max_round,
        min_amount=min_pack_price - 1,
        txn_type="pay",
    )


def search_transactions(
    note_prefix: str,
    storage_metadata: StorageMetadata,
    params,
    min_pack_price: int,
    chunk_size: int = 10000,
):
    # Initialize variables
    min_round = storage_metadata.last_processed_block
    max_round = params.first

    if min_round == max_round:
        return []

    if min_round > max_round:
        raise ValueError(f"min_round ({min_round}) > max_round ({max_round})")

    transactions = []
    last_min = min_round

    while True:
        try:
            # Iterate through the rounds in chunks
            for start in range(min_round, max_round + 1, chunk_size):
                end = start + chunk_size - 1
                response = _get_transactions_between_rounds(
                    note_prefix, start, end, min_pack_price, chunk_size
                )
                chunk_transactions = (
                    response["transactions"] if "transactions" in response else []
                )

                last_min = start

                if len(chunk_transactions) == 0:
                    continue
                else:
                    transactions.extend(chunk_transactions)

            break

        except Exception as e:
            if chunk_size <= 10:
                raise e

            chunk_size = math.ceil(chunk_size // 2)  # Decrease the chunk size
            min_round = last_min

            continue  # Retry with the smaller chunk size

    return transactions


def _close_swap(
    asset_sender: LogicSigWallet,
    asset_receiver: Wallet,
    asset_close_to: Wallet,
    asset_ids: list[int],
    swapper_funds_sender: LogicSigWallet,
    swapper_funds_receiver: Wallet,
    swapper_funds_close_to: Wallet,
    proof_sender: Wallet,
    proof_receiver: Wallet,
    asset_amt: int = 0,
    swapper_funds_amt: int = 0,
    proof_amt: int = 0,
):
    """
    Close a swap by sending the funds back to the original sender.
    """

    params = algod_client.suggested_params()

    signers = []
    transactions = []

    for asset_id in asset_ids:
        transactions.append(
            AssetTransferTxn(
                sender=asset_sender.public_key,
                sp=params,
                receiver=asset_receiver.public_key,
                amt=asset_amt,
                index=asset_id,
                close_assets_to=asset_close_to.public_key,
            )
        )
        signers.append(asset_sender)

    transactions.append(
        PaymentTxn(
            sender=swapper_funds_sender.public_key,
            sp=params,
            receiver=swapper_funds_receiver.public_key,
            amt=swapper_funds_amt,
            close_remainder_to=swapper_funds_close_to.public_key,
        )
    )
    signers.append(swapper_funds_sender)

    transactions.append(
        PaymentTxn(
            sender=proof_sender.public_key,
            sp=params,
            receiver=proof_receiver.public_key,
            amt=proof_amt,
        )
    )
    signers.append(proof_sender)

    gtx_id, _ = group_sign_send_wait(algod_client, signers, transactions)

    pretty_print(f"\n --- Account {proof_sender.public_key} closed city pack.")

    return gtx_id


def _resolve_already_purchased():
    available_packs = load_packs(CITY_PACK_AVAILABLE_PATH)
    available_pack_ids = [pack.id for pack in available_packs]
    purchased_packs = load_packs(CITY_PACK_PURCHASED_PATH)

    for pack in purchased_packs:
        if pack.id in available_pack_ids:
            pack_to_remove = [
                pack_to_remove
                for pack_to_remove in available_packs
                if pack_to_remove.id == pack.id
            ][0]
            available_packs.remove(pack_to_remove)

    save_packs(CITY_PACK_AVAILABLE_PATH, available_packs)


_resolve_already_purchased()

operation = "pp"  # 'pp' for pack purchase
note_decoded = f"awe_{operation}_"
note_prefix = note_decoded.encode()

awt_testnet_index = 51363057
card_index = 18725886

manager_pkey = mnemonic.to_private_key(MANAGER_PASSPHRASE)
manager_address = mnemonic.to_public_key(MANAGER_PASSPHRASE)
manager_wallet = Wallet(private_key=manager_pkey, public_key=manager_address)

last_processed_block = load(CITY_PACK_METADATA_PATH)
storage_metadata = (
    StorageMetadata(**last_processed_block)
    if last_processed_block
    else StorageMetadata(algod_client.suggested_params().first)
)


params = algod_client.suggested_params()
min_pack_price = 5_000_000
latest_pack_purchase_txns = search_transactions(
    note_prefix=note_prefix,
    storage_metadata=storage_metadata,
    params=params,
    min_pack_price=min_pack_price,
)


if len(latest_pack_purchase_txns) == 0:
    pretty_print("No new transactions to process")
    storage_metadata.last_processed_block = params.first
    save_metadata(CITY_PACK_METADATA_PATH, storage_metadata)
    exit(0)


for index, pack_purchase_txn in enumerate(latest_pack_purchase_txns):
    available_packs = load_packs(CITY_PACK_AVAILABLE_PATH)
    purchased_packs = load_packs(CITY_PACK_PURCHASED_PATH)

    pretty_print(
        f"last processed block for city pack closeouts {storage_metadata.last_processed_block}"
    )
    pretty_print(f"Running against {LEDGER_TYPE}")

    pack_purchase_note = decode_city_pack_note(pack_purchase_txn["note"])

    if len(latest_pack_purchase_txns) - 1 == index:
        confirmed_round = (
            pack_purchase_txn["confirmed-round"]
            if "confirmed-round" in pack_purchase_txn
            else pack_purchase_txn["transaction"]["confirmed-round"]
            if "confirmed-round" in pack_purchase_txn["transaction"]
            else None
        )
        if confirmed_round:
            storage_metadata.last_processed_block = confirmed_round
            save_metadata(CITY_PACK_METADATA_PATH, storage_metadata)

    if pack_purchase_note:
        sender_mismatch = (
            pack_purchase_txn["sender"] != pack_purchase_note.buyer_address
        )

        pack_available = pack_purchase_note.pack_id in [
            pack.id for pack in available_packs
        ]

        pack_purchased = pack_purchase_note.pack_id in [
            pack.id for pack in purchased_packs
        ]

        if sender_mismatch:
            pretty_print(
                f"Sender mismatch for pack purchase {pack_purchase_txn['id']} - {pack_purchase_txn['sender']} != {pack_purchase_note.buyer_address}"
            )

        elif pack_purchased:
            pretty_print(
                f"Pack ${pack_purchase_note.pack_id} already purchased, skipping"
            )

        elif not pack_available:
            pretty_print(
                f"Pack {pack_purchase_note.pack_id} is not in list of available packs - verify manually"
            )

        else:
            try:
                pack_to_close: CityPack = [
                    pack
                    for pack in available_packs
                    if pack.id == pack_purchase_note.pack_id
                ][0]

                escrow_lsig = LogicSig(base64.b64decode(pack_to_close.contract))
                escrow_wallet = LogicSigWallet(
                    logicsig=escrow_lsig, public_key=escrow_lsig.address()
                )

                gtxn_id = pack_purchase_txn.get("id")

                try:
                    gtxn_id = _close_swap(
                        asset_sender=escrow_wallet,
                        asset_receiver=manager_wallet,
                        asset_close_to=manager_wallet,
                        asset_ids=[asset["id"] for asset in pack_to_close.offered_asas],
                        swapper_funds_sender=escrow_wallet,
                        swapper_funds_receiver=manager_wallet,
                        swapper_funds_close_to=manager_wallet,
                        proof_sender=manager_wallet,
                        proof_receiver=manager_wallet,
                    )
                except Exception as e:
                    pretty_print(
                        f"Failed to close swap for {gtxn_id} - {e}. Was most probably processed but not persisted, proceeding with obtained tx id {gtxn_id}"
                    )

                tx = indexer.transaction(gtxn_id)

                confirmed_round = (
                    tx["transaction"]["confirmed-round"]
                    if "confirmed-round" in tx["transaction"]
                    else None
                )
                storage_metadata.last_processed_block = confirmed_round

                if confirmed_round:
                    pretty_print(f"Closed pack {pack_purchase_note.pack_id} {gtxn_id}")
                    purchased_packs.append(pack_to_close)
                    available_packs.remove(pack_to_close)
                    save_packs(CITY_PACK_AVAILABLE_PATH, available_packs)
                    save_packs(CITY_PACK_PURCHASED_PATH, purchased_packs)
                    save_metadata(CITY_PACK_METADATA_PATH, storage_metadata)

                    try:
                        notify_citypack_purchase(pack_to_close)
                    except Exception as e:
                        pretty_print(f"Failed to notify city pack purchase {e}")

            except Exception as exp:
                pretty_print(f"Error processing city closeout: {exp}")
