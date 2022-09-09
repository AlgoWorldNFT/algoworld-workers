from os import environ

from algosdk import account, mnemonic
from tinyman.v1.client import TinymanMainnetClient, TinymanTestnetClient

from src.shared.common import LEDGER_TYPE, algod_client

SWAP_REWARDS_PASSPHRASE = environ.get("SWAP_REWARDS_PASSPHRASE")
swap_rewards_pkey = mnemonic.to_private_key(SWAP_REWARDS_PASSPHRASE)
swap_rewards_address = account.address_from_private_key(swap_rewards_pkey)

Tinyman = (
    TinymanMainnetClient if LEDGER_TYPE.lower() == "mainnet" else TinymanTestnetClient
)
client = Tinyman(algod_client=algod_client, user_address=swap_rewards_address)

AWT_ID = 51363057 if LEDGER_TYPE.lower() == "testnet" else 233939122
AWT = client.fetch_asset(AWT_ID)
TMP_POOL = client.fetch_asset(552685784)  # TODO: fix for testnet as well
ALGO = client.fetch_asset(0)

# Fetch the pool we will work with
pool = client.fetch_pool(AWT, ALGO)


account_info = algod_client.account_info(address=swap_rewards_address)
account_info_algo_balance = account_info["amount"]

if account_info_algo_balance < 3 * 1e6:
    print(f"Not enough ALGO to deposit liquidity. Need at least 3 ALGO. Skipping...")
    exit(0)

account_info_awt_balance = list(
    filter(lambda x: (x["asset-id"] == AWT_ID), account_info["assets"])
)[0]

purchase_amount = account_info_algo_balance - account_info["min-balance"] - 1e6
quote = pool.fetch_mint_quote(
    ALGO(purchase_amount),
    slippage=0.01,
)

print(f"Swapping {quote.amounts_in} to {quote.liquidity_asset_amount_with_slippage}")

# Prepare a transaction group
transaction_group = pool.prepare_mint_transactions_from_quote(quote)
# Sign the group with our key
transaction_group.sign_with_private_key(swap_rewards_address, swap_rewards_pkey)
# Submit transactions to the network and wait for confirmation
result = client.submit(transaction_group, wait=True)

# Check if any excess remaining after the swap
excess = pool.fetch_excess_amounts()
if AWT in excess:
    amount = excess[AWT]
    print(f"Excess: {amount}")
    # We might just let the excess accumulate rather than redeeming if its < 1 TinyUSDC
    if amount > 1_000_000:
        transaction_group = pool.prepare_redeem_transactions(amount)
        transaction_group.sign_with_private_key(swap_rewards_address, swap_rewards_pkey)
        result = client.submit(transaction_group, wait=True)
        print(f"Redeemed excess: {amount} {result}")


info = pool.fetch_pool_position()
share = info["share"] * 100
print(f"Pool Tokens: {info[pool.liquidity_asset]}")
print(f"Assets: {info[AWT]}, {info[ALGO]}")
print(f"Share of pool: {share:.3f}%")
