import os
import requests
from bs4 import BeautifulSoup
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

def fetch_recent_activity(steamid):
    url = f"https://steamcommunity.com/profiles/{steamid}"

    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/138.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://steamcommunity.com/",
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=10,
        )

        logger.info(f"Steam Community Status: {response.status_code}")

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        recent = soup.select_one(".recent_game")

        if not recent:
            logger.warning("No recent activity found.")
            return None

        game_name = recent.select_one(".game_name").get_text(strip=True)

        store_link = recent.select_one(".game_name a")

        appid = None

        if store_link:
            try:
                appid = int(store_link["href"].rstrip("/").split("/")[-1])
            except (ValueError, IndexError):
                logger.warning("Failed to parse App ID from Steam profile.")

        return {
            "game": game_name,
            "appid": appid
        }

    except Exception as e:
        logger.error(f"Recent activity scrape failed: {e}")
        return None
    
    
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
        user_resp.raise_for_status()
        user = user_resp.json()["response"]["players"][0]

        # Steam Level
        level_resp = requests.get(
            f"{base_url}/IPlayerService/GetSteamLevel/v1/?steamid={steamid}&key={key}",
            timeout=10,
        )
        level_resp.raise_for_status()
        level = str(level_resp.json()["response"]["player_level"])

        # Owned Games
        games_resp = requests.get(
            f"{base_url}/IPlayerService/GetOwnedGames/v1/?steamid={steamid}&include_appinfo=1&include_played_free_games=1&key={key}",
            timeout=10,
        )
        games_resp.raise_for_status()
        games = games_resp.json()["response"]
        
        # Recently Played (only used for 2-week playtime)
        recent_resp = requests.get(
            f"{base_url}/IPlayerService/GetRecentlyPlayedGames/v1/?steamid={steamid}&key={key}",
            timeout=10,
        )
        recent_resp.raise_for_status()
        recent = recent_resp.json()["response"]
        
        #Recent Activity
        recent_activity = fetch_recent_activity(steamid)
        
        # Friends
        friends_resp = requests.get(
            f"{base_url}/ISteamUser/GetFriendList/v1/?steamid={steamid}&relationship=friend&key={key}",
            timeout=10,
        )
        friends_resp.raise_for_status()
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
        for game in recent.get("games", [])
    )

    recent_game = "None"
    recent_game_icon = ""

    if recent_activity:
        recent_game = recent_activity["game"]

        appid = recent_activity["appid"]

        matched_game = next(
            (
                game
                for game in games.get("games", [])
                if game["appid"] == appid
            ),
            None,
        )

        if matched_game and matched_game.get("img_icon_url"):
            recent_game_icon = (
                "https://media.steampowered.com/"
                "steamcommunity/public/images/apps/"
                f"{appid}/"
                f"{matched_game['img_icon_url']}.jpg"
            )

    vanity = user["profileurl"].rstrip("/").split("/")[-1]

    member_since = str(
        datetime.utcfromtimestamp(user["timecreated"]).year
    )

    friend_count = len(
        friends.get("friendslist", {}).get("friends", [])
    )

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
                    "name": "steam_recently_played",
                    "value": recent_game
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
                    "name": "steam_friends",
                    "value": str(friend_count)
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