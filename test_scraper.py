import requests
from bs4 import BeautifulSoup

steamid = "76561198834729630"

url = f"https://steamcommunity.com/profiles/{steamid}"

response = requests.get(
    url,
    headers={
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/138.0 Safari/537.36"
        )
    },
)

print(f"Status: {response.status_code}")

soup = BeautifulSoup(response.text, "html.parser")

recent = soup.select_one(".recent_game")

if recent:
    print("Found recent game!")

    print(
        "Game:",
        recent.select_one(".game_name").get_text(strip=True)
    )

    print(
        "Details:",
        recent.select_one(".game_info_details").get_text(
            " ",
            strip=True,
        )
    )

    print(
        "Image:",
        recent.select_one("img")["src"]
    )

else:
    print("No recent activity found.")