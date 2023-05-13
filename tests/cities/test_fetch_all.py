from src.cities import fetch_all
from src.cities.fetch_all import fetch_aw_cities
from src.shared.models import AlgoWorldCityAsset


def test_fetch_aw_cities(mocker):
    # Arrange
    indexer_mock = mocker.Mock()

    dummy_city = AlgoWorldCityAsset(
        **{
            "index": 123,
            "name": "test123",
            "url": "ipfs://testcid",
            "influence": 123,
            "status": "test",
        }
    )
    mocker.patch(
        "src.cities.fetch_all.get_all_cities",
        return_value=[dummy_city],
    )

    save_aw_assets_patch = mocker.patch("src.cities.fetch_all.save_aw_assets")

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
                        "name": "AW #Test1",
                        "name-b64": "TmV2ZXJsYW5kIzE=",
                        "reserve": "test",
                        "total": 1,
                        "url": "test",
                        "url-b64": "dGVzdA==",
                    },
                }
            ],
            "current-round": 123,
            "next-token": "123",
        },
        {},
    ]

    # Act
    result = fetch_aw_cities(indexer_mock, "test")

    # Assert
    assert result == None
    assert save_aw_assets_patch.call_count == 1
    assert indexer_mock.search_assets.call_count == 2
    assert save_aw_assets_patch.call_args[0][1][0] == dummy_city


def test_name_equals_main(mocker):
    # Arrange
    mock_main = mocker.patch.object(fetch_all, "main", mocker.MagicMock())
    mocker.patch.object(fetch_all, "__name__", "__main__")

    # Act
    fetch_all.init()

    # Assert
    mock_main.assert_called_once()
