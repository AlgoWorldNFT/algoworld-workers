import logging

import requests

from src.shared.common import (
    ALGOWORLD_CHANNEL_ID,
    DISCORD_WEBHOOK_URL,
    TELEGRAM_API_KEY,
)
from src.shared.models import CityPack


def notify_citypack_purchase(city_pack: CityPack):
    try:
        asa_titles = ",".join(
            [
                f"\n{asset['title']} x {asset['amount']}"
                for asset in city_pack.offered_asas
            ]
        )
        data = {
            "chat_id": ALGOWORLD_CHANNEL_ID,
            "text": f"🤖 {city_pack.title} was purchased 🎉\nThis pack consisted of: <b>{asa_titles}</b> 🎉\n<a href='https://explorer.algoworld.io/packs'>View on AlgoWorldExplorer</a>",
            "parse_mode": "HTML",
        }
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_API_KEY}/sendMessage",
            data,
            timeout=10,
        )

        requests.post(
            DISCORD_WEBHOOK_URL,
            timeout=10,
            json={
                "avatar_url": "https://i.imgur.com/0qGJ2um.png",
                "embeds": [
                    {
                        "title": "New city pack purchase on AlgoWorldExplorer",
                        "url": f"https://explorer.algoworld.io/packs",
                        "description": f"🤖 **{city_pack.title}** was purchased 🎉\nThis pack consisted of: **{asa_titles}**🎉",
                        "color": 16724871,
                        "fields": [],
                    }
                ],
            },
        )

    except Exception as exp:
        logging.exception(f"Unable to report notifications {exp}")


def notify_influence_deposit(sender_address: str, influence: int, city_name: str):
    try:
        sender_wallet = sender_address[0:4] + "..." + sender_address[54:]

        data = {
            "chat_id": ALGOWORLD_CHANNEL_ID,
            "text": f"🤖 <b>{sender_wallet}</b> have deposited some AWT 💰 to <b>{city_name}</b>.\nNew influence attribute value is <b>{influence}</b> 🎉\n<a href='https://explorer.algoworld.io/leaderboard'>View on AlgoWorldExplorer</a>",
            "parse_mode": "HTML",
        }
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_API_KEY}/sendMessage",
            data,
            timeout=10,
        )

        requests.post(
            DISCORD_WEBHOOK_URL,
            timeout=10,
            json={
                "avatar_url": "https://i.imgur.com/0qGJ2um.png",
                "embeds": [
                    {
                        "title": "New city influence deposit on AlgoWorldExplorer",
                        "url": f"https://explorer.algoworld.io/leaderboard",
                        "description": f"🤖 **{sender_wallet}** have deposited some AWT 💰 to **{city_name}**.\nNew influence attribute value is **{influence}** 🎉",
                        "color": 16724871,
                        "fields": [],
                    }
                ],
            },
        )

    except Exception as exp:
        logging.exception(f"Unable to report notifications {exp}")
