import os
from os import environ
from pathlib import Path

from algosdk.v2client import algod, indexer

LEDGER_TYPE = environ.get("LEDGER_TYPE", "TestNet")

MANAGER_PASSPHRASE = os.environ.get("MANAGER_PASSPHRASE")

INDEXER_URL = (
    "https://algoindexer.testnet.algoexplorerapi.io"
    if LEDGER_TYPE.lower() == "testnet"
    else "https://algoindexer.algoexplorerapi.io"
)
ALGOD_URL = (
    "https://node.testnet.algoexplorerapi.io"
    if LEDGER_TYPE.lower() == "testnet"
    else "https://node.algoexplorerapi.io"
)

algod_client = algod.AlgodClient("", ALGOD_URL, headers={"User-Agent": "algosdk"})
indexer = indexer.IndexerClient("", INDEXER_URL, headers={"User-Agent": "algosdk"})


# Countries, Assets, Metadata
DATA_FOLDER_PATH = str(Path(Path.cwd()).joinpath("data").joinpath(LEDGER_TYPE.lower()))
PROCESSED_NOTES_PATH = f"{DATA_FOLDER_PATH}/processed_notes.json"
METADATA_PATH = f"{DATA_FOLDER_PATH}/metadata.json"
ALL_CITIES_PATH = f"{DATA_FOLDER_PATH}/all_cities.json"
CITIES_DB_PATH = f"{DATA_FOLDER_PATH}/cities_db.json"
ALL_COUNTRIES_PATH = f"{DATA_FOLDER_PATH}/all_countries.json"
COUNTRIES_DB_PATH = f"{DATA_FOLDER_PATH}/countries_db.json"

# Packs
CITY_PACKS_AMOUNT_LIMIT = os.environ.get("CITY_PACKS_AMOUNT_LIMIT", 40)
CITY_PACKS_CARD_NUMBER = os.environ.get("CITY_PACKS_CARD_NUMBER", 5)
CITY_PACKS_ALGO_PRICE = os.environ.get("CITY_PACKS_ALGO_PRICE", 10_000_000)
CITY_PACK_ASA_TO_ALGO_MIN_FEE = os.environ.get("CITY_PACK_ASA_TO_ALGO_MIN_FEE", 1_000)
CITY_PACK_BASE_OPTIN_FEE = os.environ.get("CITY_PACK_BASE_OPTIN_FEE", 210_000)
CITY_PACK_INCENTIVE_ADDRESS = (
    "RJVRGSPGSPOG7W3V7IMZZ2BAYCABW3YC5MWGKEOPAEEI5ZK5J2GSF6Y26A"
)
ACTIVE_CITY_PACKS_PATH = f"{DATA_FOLDER_PATH}/active_city_packs.json"
ARCHIVED_CITY_PACKS_PATH = f"{DATA_FOLDER_PATH}/archived_city_packs.json"
