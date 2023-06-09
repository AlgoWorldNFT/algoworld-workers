import base64

from src.countries import fetch_all
from src.countries.fetch_all import (
    fetch_aw_countries,
    fetch_country_image_txns,
    fetch_country_image_url,
)


def test_fetch_country_image_txns(mocker):
    # Arrange
    search_transactions_generic = mocker.patch(
        "src.countries.fetch_all.search_transactions_generic",
    )
    search_transactions_generic.return_value = {
        "transactions": [{"note": "test"}, {"not_note": "test"}]
    }

    # Act
    processed_txns = fetch_country_image_txns(search_transactions_generic, "test", 1)

    # Assert
    assert len(processed_txns) == 1
    assert processed_txns[0] == {"note": "test"}


def test_fetch_country_image_txns_empty(mocker):
    # Arrange
    search_transactions_generic = mocker.patch(
        "src.countries.fetch_all.search_transactions_generic",
    )
    search_transactions_generic.return_value = {}

    # Act
    processed_txns = fetch_country_image_txns(search_transactions_generic, "test", 1)

    # Assert
    assert not processed_txns


def test_fetch_country_image_url(mocker):
    # Arrange
    indexer_mock = mocker.Mock()
    expected_note_url = "ipfs://testcid"
    mocker.patch(
        "src.countries.fetch_all.fetch_country_image_txns",
        return_value=[{"note": base64.b64encode(expected_note_url.encode("utf-8"))}],
    )

    # Act
    processed_note_url = fetch_country_image_url(indexer_mock, "test", 1)

    # Assert
    assert expected_note_url in processed_note_url


def test_fetch_country_image_url_exception(mocker):
    # Arrange
    indexer_mock = mocker.Mock()
    mocker.patch(
        "src.countries.fetch_all.fetch_country_image_txns",
        return_value=[{"note": 1234}],
    )
    print_mock = mocker.patch(
        "src.countries.fetch_all.pretty_print",
    )

    # Act
    fetch_country_image_url(indexer_mock, "test", 1)

    # Assert
    print_mock.assert_called_once()


def test_fetch_aw_countries(mocker):
    # Arrange
    indexer_mock = mocker.Mock()

    fetch_country_image_url_patch = mocker.patch(
        "src.countries.fetch_all.fetch_country_image_url"
    )
    fetch_country_image_url_patch.side_effect = ["ipfs://testcid", None]

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
                        "name": "AW #Test2",
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
    result = fetch_aw_countries(indexer_mock, "test")

    # Assert
    assert len(result) == 2
    assert result[0].name == "AW #Test1"
    assert result[0].url == "ipfs://testcid"
    assert result[1].name == "AW #Test2"
    assert result[1].url == "test"


def test_name_equals_main(mocker):
    # Arrange
    mock_main = mocker.patch.object(fetch_all, "main", mocker.MagicMock())
    mocker.patch.object(fetch_all, "__name__", "__main__")

    # Act
    fetch_all.init()

    # Assert
    mock_main.assert_called_once()
