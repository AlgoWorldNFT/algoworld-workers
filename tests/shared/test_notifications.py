from src.shared.models import CityPack
from src.shared.notifications import notify_citypack_purchase, notify_influence_deposit

dummy_pack = CityPack(
    **{
        "contract": "dummy_contract",
        "creator": "TSYD5NUVJZLYB3MDFZSAVCSXDDH3ZABDDUARUDAWTU7KVMNVHCH2NQOYWE",
        "escrow": "J75PX37FTLDLVAGS6ZTHLXZMYS5YQSFHI74SROUFXYHMZB2JKVWOBFQGWE",
        "id": 3,
        "is_active": False,
        "is_closed": True,
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
    }
)


def test_notify_citypack_purchase(mocker, monkeypatch):
    # Arrange
    monkeypatch.setattr("src.shared.notifications.ALGOWORLD_CHANNEL_ID", 0)
    monkeypatch.setattr("src.shared.notifications.TELEGRAM_API_KEY", 0)
    monkeypatch.setattr("src.shared.notifications.DISCORD_WEBHOOK_URL", 0)
    post_mock = mocker.patch("src.shared.notifications.requests.post")

    # Act
    notify_citypack_purchase(dummy_pack)

    # Assert
    post_mock.call_count == 2


def test_notify_influence_deposit(mocker, monkeypatch):
    # Arrange
    dummy_sender = "TSYD5NUVJZLYB3MDFZSAVCSXDDH3ZABDDUARUDAWTU7KVMNVHCH2NQOYWE"
    post_mock = mocker.patch("src.shared.notifications.requests.post")

    # Act
    notify_influence_deposit(dummy_sender, 500, "city name")

    # Assert
    post_mock.call_count == 2
