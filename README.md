# DiscordPush

A Python script that monitors specific Discord channels and forwards messages to your iPhone through Pushover notifications. Perfect for keeping track of important messages without staying glued to Discord.

## Features

- 📱 Real-time push notifications for Discord messages
- 🎯 Monitor specific channels and users
- 📎 Support for attachments and embeds
- 🔔 Different notification priorities and sounds
- 🔄 Automatic reconnection handling
- 📊 Console logging for monitoring

## Prerequisites

- Python 3.7+
- A Discord account
- Pushover account and iOS app

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/DiscordPush.git
cd DiscordPush
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy `.env.template` to `.env` and fill in your credentials:
```bash
cp .env.template .env
```

## Configuration

Edit `.env` with your details:

```env
# Discord configuration
DISCORD_TOKEN=your_discord_token_here
CHANNEL_ID=your_channel_id_here
TARGET_USER_ID=target_user_id_here

# Pushover configuration
PUSHOVER_USER_KEY=your_pushover_user_key_here
PUSHOVER_API_TOKEN=your_pushover_api_token_here
```

### Getting the Required Values

1. Discord Token:
   - Open Discord in your web browser
   - Press F12 to open Developer Tools
   - Go to Network tab
   - Look for requests to discord.com
   - Find the "authorization" header in the request headers

2. Channel ID:
   - Enable Developer Mode in Discord Settings
   - Right-click the channel
   - Click "Copy ID"

3. User ID:
   - Enable Developer Mode in Discord Settings
   - Right-click the user
   - Click "Copy ID"

4. Pushover Credentials:
   - Create account at [pushover.net](https://pushover.net)
   - Get your User Key from the dashboard
   - Create a new application to get the API Token

## Usage

Run the script:
```bash
python discord_monitor.py
```

The script will:
1. Connect to Discord
2. Monitor the specified channel
3. Send push notifications for new messages from the target user
4. Display status in the console

## Notification Types

- **New Messages**: High priority with "cosmic" sound
- **Status Updates**: Normal priority with default sound
- **Errors**: High priority with "falling" sound

## Security Note

⚠️ **Important**: This script uses a user account token which may violate Discord's Terms of Service. Use at your own risk.

Keep your Discord token and Pushover credentials secure. Never share them or commit them to version control.

## License

MIT License - See LICENSE file for details 