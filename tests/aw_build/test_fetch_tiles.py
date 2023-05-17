from unittest.mock import MagicMock, patch

import pytest

from src.aw_build.fetch_tiles import fetch_tiles, find_list_awt_accounts
from src.shared.common import BUILD_ASSET_DB_PATH


@pytest.fixture
def indexer_mock():
    indexer_mock = MagicMock()
    return indexer_mock


def test_find_list_awt_accounts(indexer_mock):
    indexer_mock.indexer_request.return_value = {
        "balances": [{"address": "test_address_1"}, {"address": "test_address_2"}],
        "next-token": None,
    }

    result = find_list_awt_accounts(indexer_mock)
    assert result == ["test_address_1", "test_address_2"]


def test_fetch_tiles(indexer_mock):
    indexer_mock.search_assets.return_value = {
        "assets": [
            {"deleted": False},
            {"deleted": True},
            {"deleted": False},
        ],
    }
    indexer_mock.asset_balances.return_value = {
        "balances": [
            {"amount": 1, "address": "test_address_1"},
            {"amount": 0, "address": "test_address_2"},
            {"amount": 5, "address": "test_address_3"},
        ],
    }
    find_list_awt_accounts_mock = MagicMock()
    find_list_awt_accounts_mock.return_value = ["test_address_1", "test_address_3"]

    with patch(
        "src.aw_build.fetch_tiles.get_all_tiles", return_value=[{"tile": "test"}]
    ):
        with patch(
            "src.aw_build.fetch_tiles.save_tiles_assets"
        ) as save_tiles_assets_mock:
            fetch_tiles(indexer_mock, "manager_address")
            save_tiles_assets_mock.assert_called_once_with(
                BUILD_ASSET_DB_PATH, [{"tile": "test"}]
            )
