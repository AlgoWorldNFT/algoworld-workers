from src.shared.models import (
    AlgoWorldAsset,
    AlgoWorldCityAsset,
    ARC69Attribute,
    ARC69Record,
    AWECityPackPurchaseNotePrefix,
    AWENotePrefix,
    CityPack,
    CityPackAsa,
    LogicSigWallet,
    StorageMetadata,
    StorageProcessedNote,
    Wallet,
)


def test_arc_69():
    assert ARC69Attribute(trait_type="test", value="test")


def test_arc_69_record():
    assert ARC69Record(
        standard="test",
        external_url="test",
        attributes=[ARC69Attribute(trait_type="test", value="test")],
    )


def test_awe_note_prefix():
    assert AWENotePrefix(
        prefix="test",
        receiver="test",
        asset_id=1,
        influence_deposit=1,
        note_id="test",
    )


def test_awe_city_pack_purchase_note_prefix():
    assert AWECityPackPurchaseNotePrefix(
        prefix="test",
        operation="test",
        pack_id=1,
        buyer_address="test",
    )


def test_storage_processed_note():
    assert StorageProcessedNote(
        block=1,
        acfg_txn="test",
        id="test",
        deposit=1,
        influence=1,
        asset_id="test",
        asset_name="test",
        sender_address="test",
    )


def test_storage_metadata():
    assert StorageMetadata(last_processed_block=1)


def test_algo_world_asset():
    assert AlgoWorldAsset(index=1, name="test", url="test")


def test_algo_world_city_asset():
    assert AlgoWorldCityAsset(
        index=1, name="test", url="test", influence=1, status="test"
    )


def test_city_pack_asa():
    assert CityPackAsa(
        id=1,
        amount=1,
        decimals=1,
        title="test",
        url="test",
    )


def test_city_pack():
    assert CityPack(
        id=1,
        creator="test",
        escrow="test",
        contract="test",
        title="test",
        offered_asas=[
            CityPackAsa(id=1, amount=1, decimals=1, title="test", url="test")
        ],
        requested_algo_amount=1,
        requested_algo_wallet="test",
        is_active=True,
        is_closed=True,
        last_swap_tx="test",
    )


def test_logic_sig_wallet():
    assert LogicSigWallet(
        logicsig="test",
        public_key="test",
    )


def test_wallet():
    assert Wallet(
        private_key="test",
        public_key="test",
    )
