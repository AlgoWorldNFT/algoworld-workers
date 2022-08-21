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


DATA_FOLDER_PATH = str(Path(Path.cwd()).joinpath("data").joinpath(LEDGER_TYPE.lower()))
PROCESSED_NOTES_PATH = f"{DATA_FOLDER_PATH}/processed_notes.json"
METADATA_PATH = f"{DATA_FOLDER_PATH}/metadata.json"
ALL_CITIES_PATH = f"{DATA_FOLDER_PATH}/all_cities.json"
CITIES_DB_PATH = f"{DATA_FOLDER_PATH}/cities_db.json"
