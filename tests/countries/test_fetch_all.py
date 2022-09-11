import base64

from src.countries.fetch_all import fetch_aw_countries, fetch_country_image_url


def test_fetch_country_image_url(mocker):
    indexer_mock = mocker.Mock()
    expected_note_url = "ipfs://testcid"
    indexer_mock.search_transactions.return_value = {
        "transactions": [{"note": base64.b64encode(expected_note_url.encode("utf-8"))}]
    }
    processed_note_url = fetch_country_image_url(indexer_mock, "test", 1)
    assert processed_note_url == expected_note_url


def test_fetch_aw_countries(mocker):
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

    result = fetch_aw_countries(indexer_mock, "test")

    assert len(result) == 2
    assert result[0].name == "AW #Test1"
    assert result[0].url == "ipfs://testcid"
    assert result[1].name == "AW #Test2"
    assert result[1].url == "test"
