from random import sample

from algosdk import mnemonic
from algoworld_contracts.swapper.asas_to_algo_swapper import (
    AsasToAlgoSwapConfig,
    compile_stateless,
    multi_asa_swapper,
)

from src.shared.common import (
    CITY_ASSET_DB_PATH,
    CITY_PACK_ALGO_PRICE,
    CITY_PACK_AMOUNT_LIMIT,
    CITY_PACK_ASA_TO_ALGO_MIN_FEE,
    CITY_PACK_AVAILABLE_PATH,
    CITY_PACK_BASE_OPTIN_FEE,
    CITY_PACK_CARD_NUMBER,
    CITY_PACK_INCENTIVE_ADDRESS,
    MANAGER_PASSPHRASE,
    algod_client,
)
from src.shared.models import CityPack, CityPackAsa, LogicSigWallet, Wallet
from src.shared.utils import (
    load_aw_cities,
    load_packs,
    logic_signature,
    save_packs,
    swapper_deposit,
    swapper_opt_in,
)

manager_wallet = Wallet(
    mnemonic.to_private_key(MANAGER_PASSPHRASE),
    mnemonic.to_public_key(MANAGER_PASSPHRASE),
)
active_packs = load_packs(CITY_PACK_AVAILABLE_PATH)
all_cities = load_aw_cities(CITY_ASSET_DB_PATH)


if len(active_packs) < CITY_PACK_AMOUNT_LIMIT:
    all_diamond_cities = list(
        filter(lambda x: x.status == "AlgoWorld Diamond City", all_cities)
    )
    all_non_diamond_cities = list(
        filter(lambda x: x.status != "AlgoWorld Diamond City", all_cities)
    )

    packs_content = sample(all_non_diamond_cities, CITY_PACK_CARD_NUMBER - 1)
    random_diamond = sample(all_diamond_cities, 1)[0]
    packs_content.append(random_diamond)
    asa_ids_amounts = dict.fromkeys([str(city.index) for city in packs_content], 1)

    cfg = AsasToAlgoSwapConfig(
        swap_creator=manager_wallet.public_key,
        offered_asa_amounts=asa_ids_amounts,
        requested_algo_amount=CITY_PACK_ALGO_PRICE,
        max_fee=CITY_PACK_ASA_TO_ALGO_MIN_FEE,  # DO NOT MODIFY, default value
        optin_funding_amount=CITY_PACK_BASE_OPTIN_FEE * len(packs_content),
        incentive_fee_address=CITY_PACK_INCENTIVE_ADDRESS,
        incentive_fee_amount=0,  # DO NOT MODIFY, explorer expects this amount (similar to our fee for regular 1:1 asa swaps)
    )

    swapper_lsig = logic_signature(
        algod_client, compile_stateless(multi_asa_swapper(cfg))
    )

    swapper_wallet = LogicSigWallet(
        logicsig=swapper_lsig, public_key=swapper_lsig.address()
    )

    swapper_opt_in(
        algod=algod_client,
        swap_creator=manager_wallet,
        swapper_account=swapper_wallet,
        assets=[city.index for city in packs_content],
        funding_amount=CITY_PACK_BASE_OPTIN_FEE * len(packs_content),
    )

    swapper_deposit(
        algod=algod_client,
        swap_creator=manager_wallet,
        swapper_account=swapper_wallet,
        assets=asa_ids_amounts,
    )

    contract = algod_client.compile(compile_stateless(multi_asa_swapper(cfg)))

    new_pack_id = active_packs[-1].id + 1
    new_pack = CityPack(
        id=new_pack_id,
        creator=manager_wallet.public_key,
        escrow=swapper_lsig.address(),
        contract=contract["result"],
        offered_asas=[
            CityPackAsa(
                **{
                    "id": city.index,
                    "amount": 1,
                    "decimals": 0,
                    "title": city.name,
                    "url": city.url,
                }
            )
            for city in packs_content
        ],
        title=f"AW City Pack #{new_pack_id}",
        requested_algo_amount=CITY_PACK_ALGO_PRICE,
        requested_algo_wallet=None,
        is_active=True,
        is_closed=False,
        last_swap_tx=None,
    )

    active_packs.append(new_pack)
    save_packs(CITY_PACK_AVAILABLE_PATH, active_packs)

    # ChannelsNotifier.notify_new_pack(new_pack) - TODO add telegram notifier
