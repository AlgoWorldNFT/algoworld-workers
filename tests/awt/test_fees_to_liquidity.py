from pytest import raises

from src.awt import fees_to_liquidity
from src.awt.fees_to_liquidity import fees_to_awt_liquidity


def test_fees_to_awt_liquidity_below_trigger(mocker):
    # Arrange
    swap_rewards_wallet_mock = mocker.Mock()
    tinyman_client_mock = mocker.Mock()
    algod_client_mock = mocker.Mock()
    algod_client_mock.account_info.return_value = {"amount": 2 * 1e6}
    print_mock = mocker.patch(
        "src.awt.fees_to_liquidity.pretty_print",
    )

    # Act
    with raises(SystemExit) as pytest_wrapped_e:
        fees_to_awt_liquidity(
            swap_rewards_wallet_mock, tinyman_client_mock, algod_client_mock
        )

    # Assert
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 0
    assert print_mock.call_count == 1


# TODO: refine
def test_fees_to_awt_liquidity_above_trigger(mocker):
    # Arrange
    swap_rewards_wallet_mock = mocker.Mock()
    mint_quote_mock = mocker.Mock()
    mint_quote_mock.amounts_in = 3 * 1e6
    mint_quote_mock.liquidity_asset_amount_with_slippage = 1 * 1e6

    tinyman_client_mock = mocker.Mock()
    tinyman_client_mock.return_value = tinyman_client_mock

    pool_mock = mocker.Mock()
    pool_mock.fetch_mint_quote.return_value = mint_quote_mock
    pool_mock.fetch_excess_amounts.return_value = {}
    pool_mock.liquidity_asset = "test_asset"
    pool_mock.fetch_pool_position.return_value = {"share": 0, "test_asset": 0}

    tinyman_client_mock.fetch_pool.return_value = pool_mock

    algod_client_mock = mocker.Mock()
    algod_client_mock.account_info.return_value = {
        "amount": 5 * 1e6,
        "min-balance": 0.02 * 1e6,
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
    }
    print_mock = mocker.patch(
        "src.awt.fees_to_liquidity.pretty_print",
    )

    # Act
    fees_to_awt_liquidity(
        swap_rewards_wallet_mock, tinyman_client_mock, algod_client_mock
    )

    # Assert
    assert print_mock.call_count == 3


def test_name_equals_main(mocker):
    # Arrange
    mock_main = mocker.patch.object(fees_to_liquidity, "main", mocker.MagicMock())
    mocker.patch.object(fees_to_liquidity, "__name__", "__main__")

    # Act
    fees_to_liquidity.init()

    # Assert
    mock_main.assert_called_once()
