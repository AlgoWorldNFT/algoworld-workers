from os import environ

from algosdk import mnemonic
from algosdk.v2client.algod import AlgodClient
from tinyman.v1.client import TinymanClient, TinymanMainnetClient, TinymanTestnetClient

from src.shared.common import LEDGER_TYPE, algod_client
from src.shared.models import Wallet
from src.shared.utils import pretty_print


def fees_to_awt_liquidity(
    swap_rewards_wallet: Wallet,
    tinyman_client: TinymanClient,
    algod_client: AlgodClient,
):
    AWT_ID = 51363057 if LEDGER_TYPE.lower() == "testnet" else 233939122
    AWT = tinyman_client.fetch_asset(AWT_ID)
    TMP_POOL = tinyman_client.fetch_asset(552685784)  # TODO: fix for testnet as well
    ALGO = tinyman_client.fetch_asset(0)

    # Fetch the pool we will work with
    pool = tinyman_client.fetch_pool(AWT, ALGO)

    account_info = algod_client.account_info(address=swap_rewards_wallet.public_key)
    account_info_algo_balance = account_info["amount"]

    if account_info_algo_balance < 3 * 1e6:
        pretty_print(
            f"Not enough ALGO to deposit liquidity. Need at least 3 ALGO. Skipping..."
        )
        exit(0)

    purchase_amount = account_info_algo_balance - account_info["min-balance"] - 1e6
    quote = pool.fetch_mint_quote(
        ALGO(purchase_amount),
        slippage=0.01,
    )

    pretty_print(
        f"Swapping {quote.amounts_in} to {quote.liquidity_asset_amount_with_slippage}"
    )

    # Prepare a transaction group
    transaction_group = pool.prepare_mint_transactions_from_quote(quote)
    # Sign the group with our key
    transaction_group.sign_with_private_key(
        swap_rewards_wallet.public_key, swap_rewards_wallet.private_key
    )
    # Submit transactions to the network and wait for confirmation
    result = tinyman_client.submit(transaction_group, wait=True)

    # Check if any excess remaining after the swap
    excess = pool.fetch_excess_amounts()
    if AWT in excess:
        amount = excess[AWT]
        pretty_print(f"Excess: {amount}")
        # We might just let the excess accumulate rather than redeeming if its < 1 AWT
        if amount > 1_000_000:
            transaction_group = pool.prepare_redeem_transactions(amount)
            transaction_group.sign_with_private_key(
                swap_rewards_wallet.public_key, swap_rewards_wallet.private_key
            )
            result = tinyman_client.submit(transaction_group, wait=True)
            pretty_print(f"Redeemed excess: {amount} {result}")

    info = pool.fetch_pool_position()
    share = info["share"] * 100
    pretty_print(f"Pool Tokens: {info[pool.liquidity_asset]}")
    pretty_print(f"Share of pool: {share:.3f}%")


def main():  # pragma: no cover
    passphrase = environ.get("SWAP_REWARDS_PASSPHRASE")
    swap_rewards_wallet = Wallet(
        mnemonic.to_private_key(passphrase), mnemonic.to_public_key(passphrase)
    )
    Tinyman = (
        TinymanMainnetClient
        if LEDGER_TYPE.lower() == "mainnet"
        else TinymanTestnetClient
    )
    tinyman_client = Tinyman(
        algod_client=algod_client, user_address=swap_rewards_wallet.public_key
    )

    fees_to_awt_liquidity(swap_rewards_wallet, tinyman_client, algod_client)


def init():
    if __name__ == "__main__":
        main()


init()
