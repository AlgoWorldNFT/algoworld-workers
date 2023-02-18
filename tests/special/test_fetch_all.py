from src.special import fetch_all
from src.special.fetch_all import fetch_aw_special_cards


def test_fetch_aw_special_cards(mocker):
    # Arrange
    indexer_mock = mocker.Mock()

    fetch_country_image_url_patch = mocker.patch(
        "src.countries.fetch_all.fetch_country_image_url"
    )
    fetch_country_image_url_patch.side_effect = ["ipfs://testcid", None]
    save_aw_assets_patch = mocker.patch("src.special.fetch_all.save_aw_assets")
    print_mock = mocker.patch("src.special.fetch_all.pretty_print")

    indexer_mock.search_assets.side_effect = [
        {
            "assets": [
                {
                    "created-at-round": 123,
                    "deleted": False,
                    "index": 123,
                    "params": {
                        "clawback": "test",
                        "creator": "test",
                        "decimals": 0,
                        "default-frozen": False,
                        "freeze": "test",
                        "manager": "test",
                        "name": "AW Special Card #Test1",
                        "name-b64": "TmV2ZXJsYW5kIzE=",
                        "reserve": "test",
                        "total": 1,
                        "url": "test",
                        "url-b64": "dGVzdA==",
                    },
                },
                {
                    "created-at-round": 124,
                    "deleted": False,
                    "index": 124,
                    "params": {
                        "clawback": "test",
                        "creator": "test",
                        "decimals": 0,
                        "default-frozen": False,
                        "freeze": "test",
                        "manager": "test",
                        "name": "AW Special Card #Test2",
                        "name-b64": "TmV2ZXJsYW5kIzE=",
                        "reserve": "test",
                        "total": 1,
                        "url": "test",
                        "url-b64": "dGVzdA==",
                    },
                },
                {
                    "created-at-round": 124,
                    "deleted": False,
                    "index": 124,
                    "params": {
                        "clawback": "test",
                        "creator": "test",
                        "decimals": 0,
                        "default-frozen": False,
                        "freeze": "test",
                        "manager": "test",
                        "name-b64": "TmV2ZXJsYW5kIzE=",
                        "reserve": "test",
                        "total": 1,
                        "url": "test",
                        "url-b64": "dGVzdA==",
                    },
                },
            ],
            "current-round": 123,
            "next-token": "123",
        },
        {},
    ]

    # Act
    fetch_aw_special_cards(indexer_mock, "test")

    # Assert
    assert save_aw_assets_patch.call_count == 1
    assert save_aw_assets_patch.call_args.args[1][0].name == "AW Special Card #Test1"
    assert save_aw_assets_patch.call_args.args[1][1].name == "AW Special Card #Test2"
    assert print_mock.call_count == 1


def test_name_equals_main(mocker):
    # Arrange
    mock_main = mocker.patch.object(fetch_all, "main", mocker.MagicMock())
    mocker.patch.object(fetch_all, "__name__", "__main__")

    # Act
    fetch_all.init()

    # Assert
    mock_main.assert_called_once()
