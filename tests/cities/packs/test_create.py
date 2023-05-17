from src.cities.packs import create
from src.cities.packs.create import _get_max_id, create_city_pack
from src.shared.models import AlgoWorldCityAsset, CityPack


def test_get_max_id(mocker):
    active_packs_mock = [
        CityPack(
            **{
                "contract": "dummy_contract",
                "creator": "TSYD5NUVJZLYB3MDFZSAVCSXDDH3ZABDDUARUDAWTU7KVMNVHCH2NQOYWE",
                "escrow": "GI3OQ7K66DM4RLXAVQR4LGUULN4BZH5HSFDCIVMC4BTCDCQUNAYNAGX6ZY",
                "id": 2,
                "is_active": True,
                "is_closed": False,
                "last_swap_tx": None,
                "offered_asas": [
                    {
                        "amount": 1,
                        "decimals": 0,
                        "id": 18725926,
                        "title": "AWC #6 - Chicago, USA",
                        "url": "www.algoworld-nft.com",
                    }
                ],
                "requested_algo_amount": 10000000,
                "requested_algo_wallet": None,
                "title": "AW City Pack #2",
            },
        )
    ]
    purchased_packs_mock = [
        CityPack(
            **{
                "contract": "dummy_contract_2",
                "creator": "TSYD5NUVJZLYB3MDFZSAVCSXDDH3ZABDDUARUDAWTU7KVMNVHCH2NQOYWE",
                "escrow": "J75PX37FTLDLVAGS6ZTHLXZMYS5YQSFHI74SROUFXYHMZB2JKVWOBFQGWE",
                "id": 99,
                "is_active": True,
                "is_closed": False,
                "last_swap_tx": None,
                "offered_asas": [
                    {
                        "amount": 1,
                        "decimals": 0,
                        "id": 18893065,
                        "title": "AWC #9 - Paris, France",
                        "url": "www.algoworld-nft.com",
                    },
                ],
                "requested_algo_amount": 10000000,
                "requested_algo_wallet": None,
                "title": "AW City Pack #3",
            },
        )
    ]

    assert _get_max_id(active_packs_mock, purchased_packs_mock) == 99
    assert _get_max_id([], purchased_packs_mock) == 99
    assert _get_max_id(active_packs_mock, []) == 2
    assert _get_max_id([], []) == 1


def test_create_city_pack_below_threshold(mocker, monkeypatch):
    # Arrange
    manager_wallet_mock = mocker.Mock()
    load_packs_mock = mocker.patch("src.cities.packs.create.load_packs")
    active_packs_mock = [
        CityPack(
            **{
                "contract": "dummy_contract",
                "creator": "TSYD5NUVJZLYB3MDFZSAVCSXDDH3ZABDDUARUDAWTU7KVMNVHCH2NQOYWE",
                "escrow": "GI3OQ7K66DM4RLXAVQR4LGUULN4BZH5HSFDCIVMC4BTCDCQUNAYNAGX6ZY",
                "id": 2,
                "is_active": True,
                "is_closed": False,
                "last_swap_tx": None,
                "offered_asas": [
                    {
                        "amount": 1,
                        "decimals": 0,
                        "id": 18725926,
                        "title": "AWC #6 - Chicago, USA",
                        "url": "www.algoworld-nft.com",
                    },
                    {
                        "amount": 1,
                        "decimals": 0,
                        "id": 18725967,
                        "title": "AWC #10 - Washington D.C., USA",
                        "url": "www.algoworld-nft.com",
                    },
                    {
                        "amount": 1,
                        "decimals": 0,
                        "id": 18725394,
                        "title": "AWC #7 - London, UK",
                        "url": "www.algoworld-nft.com",
                    },
                    {
                        "amount": 1,
                        "decimals": 0,
                        "id": 18892983,
                        "title": "AWC #1 - New York City, USA",
                        "url": "www.algoworld-nft.com",
                    },
                    {
                        "amount": 1,
                        "decimals": 0,
                        "id": 22888865,
                        "title": "AWC #15 - Dubai, UAE",
                        "url": "ipfs://QmTsU6mfaxPQvywuzJRzEf2WUchvXBm47jjuyAwScW2w4C",
                    },
                ],
                "requested_algo_amount": 10000000,
                "requested_algo_wallet": None,
                "title": "AW City Pack #2",
            },
        )
    ]
    purchased_packs_mock = [
        CityPack(
            **{
                "contract": "dummy_contract_2",
                "creator": "TSYD5NUVJZLYB3MDFZSAVCSXDDH3ZABDDUARUDAWTU7KVMNVHCH2NQOYWE",
                "escrow": "J75PX37FTLDLVAGS6ZTHLXZMYS5YQSFHI74SROUFXYHMZB2JKVWOBFQGWE",
                "id": 3,
                "is_active": True,
                "is_closed": False,
                "last_swap_tx": None,
                "offered_asas": [
                    {
                        "amount": 1,
                        "decimals": 0,
                        "id": 18893065,
                        "title": "AWC #9 - Paris, France",
                        "url": "www.algoworld-nft.com",
                    },
                    {
                        "amount": 1,
                        "decimals": 0,
                        "id": 18893026,
                        "title": "AWC #5 - Tokyo, Japan",
                        "url": "www.algoworld-nft.com",
                    },
                    {
                        "amount": 1,
                        "decimals": 0,
                        "id": 18891763,
                        "title": "AWC #100 - Poissy, France",
                        "url": "www.algoworld-nft.com",
                    },
                    {
                        "amount": 1,
                        "decimals": 0,
                        "id": 18893094,
                        "title": "AWC #12 - Madrid, Spain",
                        "url": "www.algoworld-nft.com",
                    },
                    {
                        "amount": 1,
                        "decimals": 0,
                        "id": 18725916,
                        "title": "AWC #5 - Tokyo, Japan",
                        "url": "www.algoworld-nft.com",
                    },
                ],
                "requested_algo_amount": 10000000,
                "requested_algo_wallet": None,
                "title": "AW City Pack #3",
            },
        )
    ]
    load_packs_mock.side_effect = [active_packs_mock, purchased_packs_mock]
    mocker.patch("src.cities.packs.create.load_aw_cities")

    non_empty_cities_mock = mocker.patch(
        "src.cities.packs.create.filter_empty_balance_cities"
    )
    non_empty_cities_mock.return_value = [
        AlgoWorldCityAsset(
            **{
                "index": 18725876,
                "influence": 200013,
                "name": "AWC #1 - New York City, USA",
                "status": "AlgoWorld Capital",
                "url": "www.algoworld-nft.com",
            }
        )
    ]

    monkeypatch.setattr("src.cities.packs.create.CITY_PACK_AMOUNT_LIMIT", 0)

    # Act
    result = create_city_pack(manager_wallet_mock)

    # Assert
    assert result == None


def test_create_city_pack_above_threshold(mocker, monkeypatch):
    # Arrange
    manager_wallet_mock = mocker.Mock()
    load_packs_mock = mocker.patch("src.cities.packs.create.load_packs")
    active_packs_mock = [
        CityPack(
            **{
                "contract": "dummy_contract",
                "creator": "TSYD5NUVJZLYB3MDFZSAVCSXDDH3ZABDDUARUDAWTU7KVMNVHCH2NQOYWE",
                "escrow": "GI3OQ7K66DM4RLXAVQR4LGUULN4BZH5HSFDCIVMC4BTCDCQUNAYNAGX6ZY",
                "id": 2,
                "is_active": True,
                "is_closed": False,
                "last_swap_tx": None,
                "offered_asas": [
                    {
                        "amount": 1,
                        "decimals": 0,
                        "id": 18725926,
                        "title": "AWC #6 - Chicago, USA",
                        "url": "www.algoworld-nft.com",
                    },
                    {
                        "amount": 1,
                        "decimals": 0,
                        "id": 18725967,
                        "title": "AWC #10 - Washington D.C., USA",
                        "url": "www.algoworld-nft.com",
                    },
                    {
                        "amount": 1,
                        "decimals": 0,
                        "id": 18725394,
                        "title": "AWC #7 - London, UK",
                        "url": "www.algoworld-nft.com",
                    },
                    {
                        "amount": 1,
                        "decimals": 0,
                        "id": 18892983,
                        "title": "AWC #1 - New York City, USA",
                        "url": "www.algoworld-nft.com",
                    },
                    {
                        "amount": 1,
                        "decimals": 0,
                        "id": 22888865,
                        "title": "AWC #15 - Dubai, UAE",
                        "url": "ipfs://QmTsU6mfaxPQvywuzJRzEf2WUchvXBm47jjuyAwScW2w4C",
                    },
                ],
                "requested_algo_amount": 10000000,
                "requested_algo_wallet": None,
                "title": "AW City Pack #2",
            },
        )
    ]
    purchased_packs_mock = [
        CityPack(
            **{
                "contract": "dummy_contract_2",
                "creator": "TSYD5NUVJZLYB3MDFZSAVCSXDDH3ZABDDUARUDAWTU7KVMNVHCH2NQOYWE",
                "escrow": "J75PX37FTLDLVAGS6ZTHLXZMYS5YQSFHI74SROUFXYHMZB2JKVWOBFQGWE",
                "id": 1,
                "is_active": True,
                "is_closed": False,
                "last_swap_tx": None,
                "offered_asas": [
                    {
                        "amount": 1,
                        "decimals": 0,
                        "id": 18893065,
                        "title": "AWC #9 - Paris, France",
                        "url": "www.algoworld-nft.com",
                    },
                    {
                        "amount": 1,
                        "decimals": 0,
                        "id": 18893026,
                        "title": "AWC #5 - Tokyo, Japan",
                        "url": "www.algoworld-nft.com",
                    },
                    {
                        "amount": 1,
                        "decimals": 0,
                        "id": 18891763,
                        "title": "AWC #100 - Poissy, France",
                        "url": "www.algoworld-nft.com",
                    },
                    {
                        "amount": 1,
                        "decimals": 0,
                        "id": 18893094,
                        "title": "AWC #12 - Madrid, Spain",
                        "url": "www.algoworld-nft.com",
                    },
                    {
                        "amount": 1,
                        "decimals": 0,
                        "id": 18725916,
                        "title": "AWC #5 - Tokyo, Japan",
                        "url": "www.algoworld-nft.com",
                    },
                ],
                "requested_algo_amount": 10000000,
                "requested_algo_wallet": None,
                "title": "AW City Pack #3",
            },
        )
    ]
    load_packs_mock.side_effect = [active_packs_mock, purchased_packs_mock]

    mocker.patch("src.cities.packs.create.load_aw_cities")

    non_empty_cities_mock = mocker.patch(
        "src.cities.packs.create.filter_empty_balance_cities"
    )
    non_empty_cities_mock.return_value = [
        AlgoWorldCityAsset(
            **{
                "index": 18725876,
                "influence": 200013,
                "name": "asset 1",
                "status": "AlgoWorld Diamond City",
                "url": "www.algoworld-nft.com",
            }
        ),
        AlgoWorldCityAsset(
            **{
                "index": 18725877,
                "influence": 200011,
                "name": "asset 2",
                "status": "AlgoWorld Capital",
                "url": "www.algoworld-nft.com",
            }
        ),
    ]

    monkeypatch.setattr("src.cities.packs.create.CITY_PACK_AMOUNT_LIMIT", 5)
    monkeypatch.setattr("src.cities.packs.create.CITY_PACK_CARD_NUMBER", 2)

    logic_signature_mock = mocker.patch("src.cities.packs.create.logic_signature")
    logic_signature_mock.return_value = logic_signature_mock
    logic_signature_mock.address.return_value = "test_address"
    mocker.patch("src.cities.packs.create.LogicSigWallet")
    mocker.patch("src.cities.packs.create.algod_client")
    mocker.patch("src.cities.packs.create.compile_stateless")
    mocker.patch("src.cities.packs.create.multi_asa_swapper")
    opt_in_mock = mocker.patch("src.cities.packs.create.swapper_opt_in")
    deposit_mock = mocker.patch("src.cities.packs.create.swapper_deposit")
    save_packs_mock = mocker.patch("src.cities.packs.create.save_packs")

    # Act
    result = create_city_pack(manager_wallet_mock)

    # Assert
    assert result
    assert result.id == active_packs_mock[0].id + 1
    assert opt_in_mock.call_count == 1
    assert deposit_mock.call_count == 1
    assert save_packs_mock.call_count == 1


def test_name_equals_main(mocker):
    # Arrange
    mock_main = mocker.patch.object(create, "main", mocker.MagicMock())
    mocker.patch.object(create, "__name__", "__main__")

    # Act
    create.init()

    # Assert
    mock_main.assert_called_once()
