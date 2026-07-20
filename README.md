# 🎮 Discord Dynamic Steam Profile Widget

<div align="center">
  <img src="https://cdn.cloudflare.steamstatic.com/store/home/store_home_share.jpg" width="700" />
</div>

> **Real-Time Steam Discord Widget Automation powered by the Steam Web API & GitHub Actions**

Automatically synchronize your public **Steam** profile statistics with Discord's **Dynamic Profile Widget** using the **Steam Web API**, **Python**, and **GitHub Actions**. No VPS, database, or always-on server required.

---

![GitHub stars](https://img.shields.io/github/stars/SharwinRaj/Steam-Stats?style=for-the-badge)
![License](https://img.shields.io/github/license/SharwinRaj/Steam-Stats?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge)
![GitHub Actions](https://img.shields.io/github/actions/workflow/status/SharwinRaj/Steam-Stats/update.yml?style=for-the-badge)

---

## 📸 Preview

<p align="center">
  <img src="preview.png">
</p>

---

## ✨ Overview

This project fetches your public Steam profile information from the **Steam Web API**, converts it into Discord's Dynamic Widget payload format, and automatically updates your Discord profile on a schedule.

### ✅ Features

- 🎮 Steam Username
- 🖼 Profile Avatar
- ⭐ Steam Level
- 🎲 Total Owned Games
- ⏱ Total Playtime
- 📅 Playtime (Last 2 Weeks)
- 👥 Friend Count
- 🆔 Steam Vanity URL
- 📆 Steam Member Since
- 🎯 Recently Played Game
- ⚡ Fully automated updates via GitHub Actions

### 🏗 Infrastructure

- GitHub Actions
- Python 3.x
- Discord Widget API
- Steam Web API
- REST API Automation

> ✅ No VPS  
> ✅ No server  
> ✅ No database  
> ✅ Runs entirely on GitHub Actions

---

# ⚙️ How It Works

1. GitHub Actions triggers on schedule or manually.
2. `update_stats.py` fetches your Steam profile using the Steam Web API.
3. The runtime gathers your profile information, Steam level, owned games, recently played games, and friends list.
4. Everything is transformed into a Discord Dynamic Widget payload.
5. Discord API receives a secure PATCH request using your bot token.
6. Your Discord widget updates automatically.

---

# 🚀 Setup

## 1. Fork this repository

---

## 2. Create a Discord Application

> This project requires a Discord application with a Dynamic Profile Widget.

### Automatic Widget Creation

Use aamia's widget creation script:

https://gist.github.com/aamiaa/7cdd590e3949cd654758bc90bcb4710b

### Manual Widget Creation

Follow Chloe Cinders' guide:

https://chloecinders.com/blog/discord-widgets

After creating your widget, copy:

- Discord Application ID
- Discord Bot Token
- Discord User ID

---

## 3. Obtain a Steam Web API Key

Create one here:

https://steamcommunity.com/dev/apikey

You'll also need your SteamID64.

---

## 4. Add GitHub Secrets

**Repository → Settings → Secrets and variables → Actions**

| Secret | Value |
|---------|------|
| `STEAM_API_KEY` | Steam Web API Key |
| `STEAM_USER_ID` | SteamID64 |
| `DISCORD_BOT_TOKEN` | Discord Bot Token |
| `DISCORD_USER_ID` | Discord User ID |
| `DISCORD_APP_ID` | Discord Application ID |

---

## 5. Run

Open

```
Actions → Update Steam Stats → Run workflow
```

After the first successful run, GitHub automatically updates your widget every 10 minutes.

**Local development**

```bash
pip install requests
python update_stats.py
```

---

# 🧩 Widget Fields

Bind these field names in your Discord widget.

| Field | Type |
|--------|------|
| `steam_user_avatar` | Image |
| `steam_username` | Text |
| `steam_user_id` | Text |
| `steam_level` | Text |
| `steam_number_games` | Text |
| `steam_total_playtime` | Text |
| `steam_total_playtime_2week` | Text |
| `steam_member_since` | Text |
| `steam_recently_played` | Text |
| `steam_friends` | Text |

---

# 🏗 System Architecture

```mermaid
flowchart TD
    A[GitHub Scheduler] --> B[update_stats.py]
    B --> C[Steam Web API]
    C --> D[Steam Profile Data]
    B --> E[GitHub Secrets]
    E --> F[Discord Authentication]
    D --> G[Build Discord Payload]
    F --> G
    G --> H[PATCH Discord API]
    H --> I[Discord Widget]
```

---

# 🌐 APIs Used

### Steam Web API

```text
GET https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/

GET https://api.steampowered.com/IPlayerService/GetSteamLevel/v0001/

GET https://api.steampowered.com/ISteamUser/GetFriendList/v0001/

GET https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/

GET https://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/
```

### Discord Widget API

```http
PATCH https://discord.com/api/v9/applications/{APP_ID}/users/{USER_ID}/identities/0/profile
```

---

# 📦 Example Payload

```json
{
  "data": {
    "dynamic": [
      {
        "type": 3,
        "name": "steam_user_avatar",
        "value": {
          "url": "https://..."
        }
      },
      {
        "type": 1,
        "name": "steam_username",
        "value": "Sharrr"
      },
      {
        "type": 1,
        "name": "steam_level",
        "value": "57"
      },
      {
        "type": 1,
        "name": "steam_number_games",
        "value": "312"
      }
    ]
  }
}
```

---

# 🤖 GitHub Actions

Workflow

```text
.github/workflows/update.yml
```

Schedule

```yaml
schedule:
  - cron: "*/10 * * * *"
```

Manual execution is also supported from the **Actions** tab.

---

```text
Steam-Stats/
├── update_stats.py
├── preview.png
├── README.md
└── .github/
    └── workflows/
        └── update.yml
```

---

## Credits

- Steam Web API
- Discord Dynamic Widgets
- Inspired by the original widget projects by Freekillbio and contributors.

---

> This project is not affiliated with Valve or Discord.