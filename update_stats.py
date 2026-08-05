import os
import requests
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CONFIG = {
    "STEAM_API_KEY": os.environ.get("STEAM_API_KEY"),
    "STEAM_USER_ID": os.environ.get("STEAM_USER_ID"),
    "DISCORD_BOT_TOKEN": os.environ.get("DISCORD_BOT_TOKEN"),
    "DISCORD_USER_ID": os.environ.get("DISCORD_USER_ID"),
    "DISCORD_APP_ID": os.environ.get("DISCORD_APP_ID"),
}


def update_discord_widget():
    base_url = "https://api.steampowered.com"
    key = CONFIG["STEAM_API_KEY"]
    steamid = CONFIG["STEAM_USER_ID"]

    try:
        # Player Summary
        user_resp = requests.get(
            f"{base_url}/ISteamUser/GetPlayerSummaries/v0002/?steamids={steamid}&key={key}",
            timeout=10,
        )
        user = user_resp.json()["response"]["players"][0]

        # Steam Level
        level_resp = requests.get(
            f"{base_url}/IPlayerService/GetSteamLevel/v1/?steamid={steamid}&key={key}",
            timeout=10,
        )
        level = str(level_resp.json()["response"]["player_level"])

        # Owned Games
        games_resp = requests.get(
            f"{base_url}/IPlayerService/GetOwnedGames/v1/?steamid={steamid}&include_appinfo=1&include_played_free_games=1&key={key}",
            timeout=10,
        )
        games = games_resp.json()["response"]

        # Friends
        friends_resp = requests.get(
            f"{base_url}/ISteamUser/GetFriendList/v1/?steamid={steamid}&relationship=friend&key={key}",
            timeout=10,
        )
        friends = friends_resp.json()

    except Exception as e:
        logger.error(f"Steam API failure: {e}")
        return

    total_playtime = sum(
        game.get("playtime_forever", 0)
        for game in games.get("games", [])
    )

    total_playtime_2weeks = sum(
        game.get("playtime_2weeks", 0)
        for game in games.get("games", [])
    )

    owned_games = games.get("games", [])

    last_game = max(
        owned_games,
        key=lambda game: game.get("rtime_last_played", 0),
        default=None
    )

    recent_game = "Not Available"
    recent_game_icon = ""

    if last_game:
        recent_game = last_game["name"]
        appid = last_game["appid"]
        icon_hash = last_game.get("img_icon_url")

        recent_game_icon = (
            "https://media.steampowered.com/"
            "steamcommunity/public/images/apps/"
            f"{appid}/"
            f"{icon_hash}.jpg"
        )

    most_played_game = max(
        owned_games,
        key=lambda game: game.get("playtime_forever", 0),
        default=None
    )

    most_played_game_name = "Not Available"
    most_played_hours = "0h"
    most_played_icon = ""

    if most_played_game:
        most_played_game_name = most_played_game["name"]
        most_played_hours = f"{most_played_game['playtime_forever'] // 60}h"

        most_played_appid = most_played_game["appid"]
        most_played_icon_hash = most_played_game["img_icon_url"]

        most_played_icon = (
            "https://media.steampowered.com/"
            "steamcommunity/public/images/apps/"
            f"{most_played_appid}/"
            f"{most_played_icon_hash}.jpg"
        )  

    vanity = user["profileurl"].rstrip("/").split("/")[-1]

    member_since = str(
        datetime.utcfromtimestamp(user["timecreated"]).year
    )

    friend_count = len(
        friends.get("friendslist", {}).get("friends", [])
    )

    dynamic = [
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
            "value": level
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
            "value": member_since
        },
        {
            "type": 1,
            "name": "steam_friends",
            "value": str(friend_count)
        },
        {
            "type": 3,
            "name": "steam_recent_game_icon",
            "value": {
                "url": recent_game_icon
            }
        },
        {
            "type": 1,
            "name": "steam_recently_played",
            "value": recent_game
        },
        {
            "type": 1,
            "name": "steam_most_played_game",
            "value": most_played_game_name
        },
        {
            "type": 1,
            "name": "steam_most_played_hours",
            "value": most_played_hours
        },
        {
            "type": 3,
            "name": "steam_most_played_icon",
            "value": {
                "url": most_played_icon
            }
        }
    ]

        
    payload = {
        "data": {
            "dynamic": dynamic
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

    response = requests.patch(
        url,
        headers=headers,
        json=payload,
        timeout=10,
    )

    logger.info(f"Discord Status: {response.status_code}")
    logger.info(response.text)


if __name__ == "__main__":
    update_discord_widget()