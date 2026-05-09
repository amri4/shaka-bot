# Shaka Bot — Satellite 01 (Good)

> *"Truth does not change based on whether you accept it or not."*

A Discord bot based on **Shaka**, Vegapunk's Satellite 01 — the embodiment of Good, logic, and justice.

## Commands

| Command | Description |
|---|---|
| `shaka judge @user <reason>` | Pass a formal judgment on a user (stored in SQLite) |
| `shaka verdicts` | Show the 5 most recent judgments in the server |
| `shaka verdict <id>` | Look up a specific judgment by ID |
| `shaka truth` | Shaka declares a philosophical truth |
| `shaka scan @user` | Analyze a user's threat level |
| `shaka siblings` | List all six Vegapunk satellites |
| `shaka?` | Show the help menu with a select dropdown |

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/shaka-bot.git
cd shaka-bot
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure your token
```bash
cp .env.example .env
```
Edit `.env` and paste your Discord bot token:
```
DISCORD_TOKEN=your_token_here
```

### 4. Run the bot
```bash
python bot.py
```

## Database

Shaka uses a local SQLite database (`shaka.db`) to store judgments. It is created automatically on first run. Add `shaka.db` to your `.gitignore` (already included).

## Discord Developer Portal Setup

1. Go to [discord.com/developers/applications](https://discord.com/developers/applications)
2. Create a new application named **Shaka**
3. Go to **Bot** → Create a bot
4. Under **Privileged Gateway Intents**, enable:
   - **Message Content Intent**
   - **Server Members Intent**
5. Copy the token into your `.env`
6. Under **OAuth2 → URL Generator**, select `bot` scope and the following permissions:
   - Send Messages, Embed Links, Read Message History, View Channels

## Cross-bot Awareness

Shaka reacts when sibling satellite names are mentioned in chat (Lilith, Edison, Pythagoras, Atlas, York). For full cross-bot awareness, run all 6 satellite bots in the same server.
