import os
import sys
import asyncio
import discord
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get configuration from environment variables
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID', 0))
TARGET_USER_ID = int(os.getenv('TARGET_USER_ID', 0))
PUSHOVER_USER_KEY = os.getenv('PUSHOVER_USER_KEY')
PUSHOVER_API_TOKEN = os.getenv('PUSHOVER_API_TOKEN')

# Validate configuration
if not all([TOKEN, CHANNEL_ID, TARGET_USER_ID, PUSHOVER_USER_KEY, PUSHOVER_API_TOKEN]):
    print("Error: Please set all required environment variables in .env file")
    print("Required variables: DISCORD_TOKEN, CHANNEL_ID, TARGET_USER_ID, PUSHOVER_USER_KEY, PUSHOVER_API_TOKEN")
    sys.exit(1)

def send_pushover_notification(message, title=None, priority=0, sound="pushover"):
    """Send a notification via Pushover."""
    try:
        data = {
            "token": PUSHOVER_API_TOKEN,
            "user": PUSHOVER_USER_KEY,
            "message": message,
            "priority": priority,
            "sound": sound
        }
        if title:
            data["title"] = title
            
        r = requests.post("https://api.pushover.net/1/messages.json", data=data)
        if r.status_code != 200:
            print(f"Error sending notification: {r.text}")
    except Exception as e:
        print(f"Error sending notification: {e}")

class MessageMonitor(discord.Client):
    def __init__(self):
        super().__init__()
        self.target_channel = None
        self.connected = False

    async def on_ready(self):
        """Called when the client is ready and connected to Discord."""
        print(f'Connected as {self.user} (ID: {self.user.id})')
        
        # Get the target channel
        self.target_channel = self.get_channel(CHANNEL_ID)
        if not self.target_channel:
            print(f"Error: Could not find channel with ID {CHANNEL_ID}")
            await self.close()
            return

        print(f"Monitoring channel: #{self.target_channel.name}")
        print(f"Filtering messages from user ID: {TARGET_USER_ID}")
        print("Waiting for messages...")
        self.connected = True

        # Send a test notification
        send_pushover_notification(
            "Discord monitor started successfully!",
            title="Discord Monitor",
            priority=0
        )

    async def on_message(self, message):
        """Called when a message is sent in any visible channel."""
        try:
            # Check if message is in target channel and from target user
            if (message.channel.id == CHANNEL_ID and 
                message.author.id == TARGET_USER_ID):
                
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                console_msg = f"\n[{timestamp}] {message.author.name}: {message.content}"
                print(console_msg)
                
                # Prepare notification message
                push_msg = f"{message.author.name}: {message.content}"
                
                # Add attachments to notification if any
                if message.attachments:
                    attachments_text = "\n".join(f"📎 {a.url}" for a in message.attachments)
                    console_msg += f"\n{attachments_text}"
                    push_msg += f"\n{attachments_text}"
                    print(attachments_text)
                
                # Add embeds to notification if any
                if message.embeds:
                    for embed in message.embeds:
                        if embed.title:
                            embed_text = f"\n📌 {embed.title}"
                            if embed.description:
                                embed_text += f": {embed.description}"
                            console_msg += embed_text
                            push_msg += embed_text
                            print(embed_text)
                
                # Send push notification
                send_pushover_notification(
                    push_msg,
                    title=f"Discord: #{self.target_channel.name}",
                    priority=1,  # High priority for immediate delivery
                    sound="cosmic"  # Use a distinctive notification sound
                )
        
        except Exception as e:
            print(f"Error processing message: {e}")

    async def on_error(self, event, *args, **kwargs):
        """Called when an error occurs in the client."""
        error_msg = f"Error in {event}: {sys.exc_info()[1]}"
        print(error_msg)
        send_pushover_notification(
            error_msg,
            title="Discord Monitor Error",
            priority=1,
            sound="falling"
        )

    async def on_disconnect(self):
        """Called when the client disconnects from Discord."""
        self.connected = False
        disconnect_msg = "Disconnected from Discord. Attempting to reconnect..."
        print(disconnect_msg)
        send_pushover_notification(
            disconnect_msg,
            title="Discord Monitor Status",
            priority=0
        )

def main():
    """Main function to run the Discord monitor."""
    client = MessageMonitor()
    
    try:
        print("Starting Discord message monitor...")
        client.run(TOKEN)
    except discord.LoginFailure:
        error_msg = "Error: Invalid Discord token. Please check your .env file."
        print(error_msg)
        send_pushover_notification(
            error_msg,
            title="Discord Monitor Error",
            priority=1
        )
    except Exception as e:
        error_msg = f"Error: {e}"
        print(error_msg)
        send_pushover_notification(
            error_msg,
            title="Discord Monitor Error",
            priority=1
        )
    finally:
        if client.connected:
            asyncio.run(client.close())

if __name__ == "__main__":
    main() 