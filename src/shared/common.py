import os
from os import environ
from pathlib import Path

from algosdk.v2client import algod, indexer

LEDGER_TYPE = environ.get("LEDGER_TYPE", "TestNet")

MANAGER_PASSPHRASE = os.environ.get("MANAGER_PASSPHRASE")

INDEXER_URL = (
    "https://testnet-idx.algonode.cloud"
    if LEDGER_TYPE.lower() == "testnet"
    else "https://mainnet-idx.algonode.cloud"
)
ALGOD_URL = (
    "https://testnet-api.algonode.cloud"
    if LEDGER_TYPE.lower() == "testnet"
    else "https://mainnet-api.algonode.cloud"
)

algod_client = algod.AlgodClient("", ALGOD_URL, headers={"User-Agent": "algosdk"})
indexer = indexer.IndexerClient("", INDEXER_URL, headers={"User-Agent": "algosdk"})


# Root
DATA_FOLDER_PATH = str(Path(Path.cwd()).joinpath("data").joinpath(LEDGER_TYPE.lower()))

# Cities
CITY_FOLDER_PATH = f"{DATA_FOLDER_PATH}/cities"
CITY_ASSET_DB_PATH = f"{CITY_FOLDER_PATH}/database.json"

## City influence
CITY_INFLUENCE_FOLDER_PATH = f"{CITY_FOLDER_PATH}/influence"
CITY_INFLUENCE_PROCESSED_NOTES_PATH = (
    f"{CITY_INFLUENCE_FOLDER_PATH}/processed_notes.json"
)
CITY_INFLUENCE_METADATA_PATH = f"{CITY_INFLUENCE_FOLDER_PATH}/metadata.json"

## City packs
CITY_PACK_FOLDER_PATH = f"{CITY_FOLDER_PATH}/packs"
CITY_PACK_AMOUNT_LIMIT = int(os.environ.get("CITY_PACK_AMOUNT_LIMIT", 40))
CITY_PACK_CARD_NUMBER = int(os.environ.get("CITY_PACK_CARD_NUMBER", 5))
CITY_PACK_ALGO_PRICE = int(os.environ.get("CITY_PACK_ALGO_PRICE", 10_000_000))
CITY_PACK_ASA_TO_ALGO_MIN_FEE = int(
    os.environ.get("CITY_PACK_ASA_TO_ALGO_MIN_FEE", 1_000)
)
CITY_PACK_BASE_OPTIN_FEE = int(os.environ.get("CITY_PACK_BASE_OPTIN_FEE", 210_000))
CITY_PACK_INCENTIVE_ADDRESS = (
    "RJVRGSPGSPOG7W3V7IMZZ2BAYCABW3YC5MWGKEOPAEEI5ZK5J2GSF6Y26A"
)
CITY_PACK_AVAILABLE_PATH = f"{CITY_PACK_FOLDER_PATH}/available.json"
CITY_PACK_PURCHASED_PATH = f"{CITY_PACK_FOLDER_PATH}/purchased.json"
CITY_PACK_METADATA_PATH = f"{CITY_PACK_FOLDER_PATH}/metadata.json"

# Countries
COUNTRY_FOLDER_PATH = f"{DATA_FOLDER_PATH}/countries"
COUNTRY_ASSET_DB_PATH = f"{COUNTRY_FOLDER_PATH}/database.json"

# Special Cards
SPECIAL_CARDS_FOLDER_PATH = f"{DATA_FOLDER_PATH}/special"
SPECIAL_CARDS_ASSET_DB_PATH = f"{SPECIAL_CARDS_FOLDER_PATH}/database.json"

# Notifications
NOTIFICATIONS_FOLDER_PATH = f"{DATA_FOLDER_PATH}/notifications"
NOTIFICATIONS_FILE_PATH = f"{NOTIFICATIONS_FOLDER_PATH}/processed.json"
DISCORD_WEBHOOK_URL = (
    environ.get("DISCORD_WEBHOOK_URL_TESTNET")
    if LEDGER_TYPE.lower() == "testnet"
    else environ.get("DISCORD_WEBHOOK_URL_MAINNET")
)
TELEGRAM_API_KEY = (
    environ.get("TELEGRAM_API_KEY_TESTNET")
    if LEDGER_TYPE.lower() == "testnet"
    else environ.get("TELEGRAM_API_KEY_MAINNET")
)
ALGOWORLD_CHANNEL_ID = (
    environ.get("ALGOWORLD_CHANNEL_ID_TESTNET")
    if LEDGER_TYPE.lower() == "testnet"
    else environ.get("ALGOWORLD_CHANNEL_ID_MAINNET")
)
