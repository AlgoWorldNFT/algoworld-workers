from algosdk import mnemonic

from src.common import (
    LEDGER_TYPE,
    MANAGER_PASSPHRASE,
    METADATA_PATH,
    PROCESSED_NOTES_PATH,
    algod_client,
)
from src.models import StorageMetadata, StorageProcessedNote
from src.utils import load, load_notes

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


active_packs = CityPack.objects.filter(is_active=True)
if len(active_packs) < settings.CITY_PACKS_AMOUNT_LIMIT:
    swap_creator = Wallet(
        mnemonic.to_private_key(settings.CITY_MANAGER_WALLET_SECRET),
        settings.CITY_MANAGER_WALLET,
    )
    all_diamond_cities = list(
        AlgoworldCity.objects.filter(city_status="AlgoWorld Diamond City").values()
    )
    all_non_diamond_cities = list(
        AlgoworldCity.objects.exclude(city_status="AlgoWorld Diamond City").values()
    )

    packs_content = sample(all_non_diamond_cities, settings.CITY_PACKS_CARD_NUMBER - 1)
    random_diamond = sample(all_diamond_cities, 1)[0]
    packs_content.append(random_diamond)
    asa_ids_amounts = dict.fromkeys(
        [str(city["asset_id"]) for city in packs_content], 1
    )

    cfg = AsasToAlgoSwapConfig(
        swap_creator=swap_creator.public_key,
        offered_asa_amounts=asa_ids_amounts,
        requested_algo_amount=settings.CITY_PACKS_ALGO_PRICE,
        max_fee=settings.CITY_PACK_ASA_TO_ALGO_MIN_FEE,  # DO NOT MODIFY, default value
        optin_funding_amount=settings.CITY_PACK_BASE_OPTIN_FEE * len(packs_content),
        incentive_fee_address=INCENTIVE_FEE_ADDRESS,
        incentive_fee_amount=0,  # DO NOT MODIFY, explorer expects this amount (similar to our fee for regular 1:1 asa swaps)
    )

    swapper_lsig = logic_signature(compile_stateless(multi_asa_swapper(cfg)))

    swapper_wallet = LogicSigWallet(
        logicsig=swapper_lsig, public_key=swapper_lsig.address()
    )

    swapper_opt_in(
        swap_creator=swap_creator,
        swapper_account=swapper_wallet,
        assets=[city["asset_id"] for city in packs_content],
        funding_amount=settings.CITY_PACK_BASE_OPTIN_FEE * len(packs_content),
    )

    swapper_deposit(
        swap_creator=swap_creator,
        swapper_account=swapper_wallet,
        assets=asa_ids_amounts,
    )

    contract = algorand.algod.compile(compile_stateless(multi_asa_swapper(cfg)))

    new_pack_id = CityPack.objects.last().pk + 1
    new_pack = CityPack.objects.create(
        pk=new_pack_id,
        creator=swap_creator.public_key,
        escrow=swapper_lsig.address(),
        contract=contract["result"],
        offered_asas=[
            {
                "id": city["asset_id"],
                "amount": 1,
                "decimals": 0,
                "title": city["name"],
                "url": city["ipfs_address"],
            }
            for city in packs_content
        ],
        title=f"AW City Pack #{new_pack_id}",
        requested_algo_amount=settings.CITY_PACKS_ALGO_PRICE,
        requested_algo_wallet=None,
        is_active=True,
        is_closed=False,
        last_swap_tx=None,
    )

    ChannelsNotifier.notify_new_pack(new_pack)


# def update_arc_tags(
#     address: str,
#     sender_address: str,
#     address_pkey: str,
#     asset_index: int,
#     influence_deposit: int,
#     cur_arc_note: ARC69Record,
#     new_status: str,
#     new_influence: int,
# ):


#     print(

#     if cur_arc_note:
#             attribute
#             for attribute in cur_arc_note.attributes
#             if (
#                 and attribute.trait_type.lower() != "city status"


#     # Sign with secret key of creator


#         print(


# def extract_update_arc_tags(
#     address: string,
#     sender_address: string,
#     address_pkey: string,
#     asset_index: int,
#     influence_deposit: int,
#     note_id: string,
# ):

#     return new_influence, update_arc_tags(


# def process_influence_txns():

#     if len(latest_txns["transactions"]) == 0:

#     for axfer_txn in latest_txns["transactions"]:
#         if axfer_txn_note:


#                 axfer_txn_note.influence_deposit
#                 != axfer_txn["asset-transfer-transaction"]["amount"]

#             if receiver_mismatch:
#                 print(

#                 print(

#                 print(

#                 new_influence, tx = extract_update_arc_tags(

#                 if confirmed_round:
#                     print(


#                     processed_notes[axfer_txn_note.note_id] = asdict(
#                         StorageProcessedNote(
#                             axfer_txn_note.note_id,
#                             axfer_txn_note.influence_deposit,
#                             new_influence,
#                             axfer_txn_note.asset_id,
#                             asset_name,
#                             manager_address,


# def update_city_status(rogue_city: AlgoWorldCityAsset, is_capital: bool):
#     txid, _ = update_arc_tags(
#         if not is_capital
#         else "AlgoWorld Capital",

#     if txid:


# def update_capital(manager_address: str):


#     while "next-token" in created_assets:
#         all_assets.extend(

#             limit=100, creator=manager_address, next_page=created_assets["next-token"]


#         city for city in all_cities if city.status.lower() == "algoworld capital"

#     for rogue_city in rogue_cities:
#         if rogue_city:

#     if first_city:
#         if first_city.status.lower() != "algoworld capital":
