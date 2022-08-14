from os import environ

from algosdk.v2client import algod, indexer

LEDGER_TYPE = environ.get("LEDGER_TYPE", "TestNet")

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
