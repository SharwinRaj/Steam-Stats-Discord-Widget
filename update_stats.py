import os
import logging
import requests

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Configuration
CONFIG = {
    "STEAM_API_KEY": os.environ.get("STEAM_API_KEY"),
    "STEAM_USER_ID": os.environ.get("STEAM_USER_ID"),
    "DISCORD_BOT_TOKEN": os.environ.get("DISCORD_BOT_TOKEN"),
    "DISCORD_USER_ID": os.environ.get("DISCORD_USER_ID"),
    "DISCORD_APP_ID": os.environ.get("DISCORD_APP_ID"),
}

BASE_URL = "https://api.steampowered.com"


def fetch_steam_data():
    """Fetch all Steam API data."""

    key = CONFIG["STEAM_API_KEY"]
    steam_id = CONFIG["STEAM_USER_ID"]

    endpoints = {
        "user": f"{BASE_URL}/ISteamUser/GetPlayerSummaries/v0002/?steamids={steam_id}&key={key}",
        "level": f"{BASE_URL}/IPlayerService/GetSteamLevel/v0001/?steamid={steam_id}&key={key}",
        "friends": f"{BASE_URL}/ISteamUser/GetFriendList/v0001/?steamid={steam_id}&relationship=friend&key={key}",
        "games": f"{BASE_URL}/IPlayerService/GetOwnedGames/v0001/?steamid={steam_id}&include_appinfo=true&include_played_free_games=true&key={key}",
        "recent": f"{BASE_URL}/IPlayerService/GetRecentlyPlayedGames/v0001/?steamid={steam_id}&key={key}",
    }

    data = {}

    try:
        for name, url in endpoints.items():
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            result = response.json()

            if "response" in result:
                data[name] = result["response"]
            else:
                data[name] = result

        return data

    except Exception as e:
        logger.error(f"Steam API error: {e}")
        return None


def update_discord_widget():
    steam = fetch_steam_data()

    if not steam:
        return

    user = steam["user"]["players"][0]
    level = steam["level"]
    friends = steam["friends"]
    games = steam["games"]
    recent = steam["recent"]

    total_playtime = sum(
        game.get("playtime_forever", 0)
        for game in games.get("games", [])
    )

    total_playtime_2weeks = sum(
        game.get("playtime_2weeks", 0)
        for game in recent.get("games", [])
    )

    vanity = user["profileurl"].rstrip("/").split("/")[-1]

    payload = {
        "data": {
            "dynamic": [
                {
                    "type": 3,
                    "name": "steam_user_avatar",
                    "value": {
                        "url": user["avatarfull"]
                    }
                },
                {
                    "type": 1,
                    "name": "steam_username",
                    "value": user["personaname"]
                },
                {
                    "type": 1,
                    "name": "steam_user_id",
                    "value": vanity
                },
                {
                    "type": 1,
                    "name": "steam_level",
                    "value": str(level["player_level"])
                },
                {
                    "type": 1,
                    "name": "steam_number_games",
                    "value": str(games.get("game_count", 0))
                },
                {
                    "type": 1,
                    "name": "steam_total_playtime",
                    "value": f"{total_playtime // 60}h"
                },
                {
                    "type": 1,
                    "name": "steam_total_playtime_2week",
                    "value": f"{total_playtime_2weeks // 60}h"
                },
                {
                    "type": 1,
                    "name": "steam_member_since",
                    "value": str(
                        __import__("datetime")
                        .datetime.utcfromtimestamp(user["timecreated"])
                        .year
                    )
                },
                {
                    "type": 1,
                    "name": "steam_recently_played",
                    "value": (
                        recent.get("games", [{}])[0].get("name", "None")
                    )
                },
                {
                    "type": 1,
                    "name": "steam_friends",
                    "value": str(
                        len(
                            friends.get("friendslist", {})
                            .get("friends", [])
                        )
                    )
                }
            ]
        }
    }

    url = (
        f"https://discord.com/api/v9/applications/"
        f"{CONFIG['DISCORD_APP_ID']}/users/"
        f"{CONFIG['DISCORD_USER_ID']}/identities/0/profile"
    )

    headers = {
        "Authorization": f"Bot {CONFIG['DISCORD_BOT_TOKEN']}",
        "Content-Type": "application/json",
    }

    response = requests.patch(url, headers=headers, json=payload, timeout=10)

    if response.status_code in (200, 204):
        logger.info("Successfully synced to Discord!")
    else:
        logger.error(f"Discord API error: {response.text}")


if __name__ == "__main__":
    update_discord_widget()