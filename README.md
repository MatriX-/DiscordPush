# Discord Prize Monitor

A web application for monitoring Discord channels and receiving notifications via Pushover. This application allows you to track messages from specific users in designated channels and receive instant notifications when they post content matching your configured filters.

## Features

- **Web-Based Configuration**: Easily manage monitored channels, users, and notification settings through a web interface
- **Customizable Filters**: Set up filters for keywords, links, and image types
- **Real-Time Notifications**: Receive instant Pushover notifications for matching messages
- **Message Dashboard**: View recent message history and monitor filter effectiveness
- **Flexible Notification Settings**: Configure notification priorities and sounds

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/discord_prize.git
cd discord_prize
```

2. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your configuration:
```env
DISCORD_TOKEN=your_discord_bot_token
CHANNEL_IDS=channel_id1,channel_id2
TARGET_USER_IDS=user_id1,user_id2
PUSHOVER_USER_KEY=your_pushover_user_key
PUSHOVER_API_TOKEN=your_pushover_api_token
```

4. Start the application:
```bash
uvicorn app.main:app --host=0.0.0.0 --port=7777
```

## API Endpoints

The application provides the following API endpoints:

- `GET /api/status`: Get Discord client connection status
- `GET /api/messages`: Get recent message history
- `GET /api/config`: Get current configuration
- `PUT /api/config/filters`: Update filter configuration
- `PUT /api/config/notifications`: Update notification settings
- `PUT /api/config/channels`: Update monitored channels
- `PUT /api/config/users`: Update target users

## Configuration

### Discord Setup
1. Create a Discord application at https://discord.com/developers/applications
2. Create a bot and get its token
3. Add the bot to your server with appropriate permissions

### Pushover Setup
1. Create a Pushover account at https://pushover.net
2. Create an application to get an API token
3. Get your user key from your account

## Development

The project is structured as follows:

```
discord_prize/
├── backend/
│   ├── app/
│   │   ├── discord/     # Discord client implementation
│   │   ├── models/      # Data models and configuration
│   │   ├── routers/     # API endpoints
│   │   ├── services/    # External services (Pushover)
│   │   └── main.py      # Application entry point
│   └── requirements.txt
├── .replit              # Replit configuration
├── replit.nix          # Replit Nix configuration
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 