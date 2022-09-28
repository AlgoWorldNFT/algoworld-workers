from re import A
from src.awt import fees_to_liquidity
from src.awt.fees_to_liquidity import fees_to_awt_liquidity
from pytest import raises


def test_fees_to_awt_liquidity_below_trigger(mocker):

    # Arrange
    swap_rewards_wallet_mock = mocker.Mock()
    tinyman_client_mock = mocker.Mock()
    algod_client_mock = mocker.Mock()
    algod_client_mock.account_info.return_value = {"amount": 2 * 1e6}
    print_mock = mocker.patch(
        "src.awt.fees_to_liquidity.print",
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


def test_fees_to_awt_liquidity_above_trigger(mocker):

    # Arrange
    swap_rewards_wallet_mock = mocker.Mock()
    tinyman_client_mock = mocker.Mock()
    tinyman_client_mock.fetch_pool.fetch_mint_quote.return_value = MintQuote()
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
        "src.awt.fees_to_liquidity.print",
    )

    # Act
    fees_to_awt_liquidity(
        swap_rewards_wallet_mock, tinyman_client_mock, algod_client_mock
    )

    # Assert
    assert print_mock.call_count == 1


def test_name_equals_main(mocker):
    # Arrange
    mock_main = mocker.patch.object(fees_to_liquidity, "main", mocker.MagicMock())
    mocker.patch.object(fees_to_liquidity, "__name__", "__main__")

    # Act
    fees_to_liquidity.init()

    # Assert
    mock_main.assert_called_once()
