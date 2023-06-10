import os
from os import environ
from pathlib import Path

from algosdk.v2client import algod, indexer

LEDGER_TYPE = environ.get("LEDGER_TYPE", "TestNet")

MANAGER_PASSPHRASE = os.environ.get("MANAGER_PASSPHRASE")
BUILD_MANAGER_PASSPHRASE = os.environ.get("BUILD_MANAGER_PASSPHRASE")

AWT_ID = 51363057 if LEDGER_TYPE.lower() == "testnet" else 233939122

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

# Build
OWNER_FEE_PC = 0.5
BUILD_FOLDER_PATH = f"{DATA_FOLDER_PATH}/aw_build"
BUILD_REWARDS_TIMESTAMP = f"{BUILD_FOLDER_PATH}/last_run.txt"
BUILD_ASSET_DB_PATH = f"{BUILD_FOLDER_PATH}/database.json"
BUILD_PROCESSED_NOTES_PATH = f"{BUILD_FOLDER_PATH}/processed_notes.json"
BUILD_METADATA_PATH = f"{BUILD_FOLDER_PATH}/metadata.json"
BUILD_ASSET = (
    [
        211484229,
        211484310,
        211484438,
        211484517,
        211484558,
        211484611,
        211484654,
        211484743,
        211484786,
        211484827,
        211484842,
        211484896,
        211485014,
        211485067,
        211485114,
        211485118,
        211485133,
        211485140,
        211485193,
        211485272,
        211485314,
        211485403,
        211485445,
        211485449,
        211485461,
        211485501,
        211485506,
        211485519,
        211485637,
        211485687,
        211485689,
        211485691,
        211485694,
        211485745,
        211485787,
        211485837,
    ]
    if LEDGER_TYPE.lower() == "testnet"
    else [
        1104974285,
        1104974346,
        1104974387,
        1104974470,
        1104974506,
        1104974547,
        1104974594,
        1104974643,
        1104974684,
        1104974706,
        1104974732,
        1104974789,
        1104974821,
        1104974852,
        1104974886,
        1104974895,
        1104974965,
        1104974990,
        1104975045,
        1104975065,
        1104975101,
        1104975132,
        1104975153,
        1104975205,
        1104975265,
        1104975361,
        1104975387,
        1104975420,
        1104975501,
        1104975551,
        1104975575,
        1104975624,
        1104975760,
        1104975802,
        1104975948,
        1104975977,
    ]
)

KEYLIST_MAP = [
    "Meadow",
    "Forest",
    "Water",
    "House",
    "Castle",
    "CityBlock",
    "ArcdeTriomphe",
    "WhiteHouse",
    "MountRushmore",
    "Colosseum",
]
AWT_TOTAL_REWARDS = 1000

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
