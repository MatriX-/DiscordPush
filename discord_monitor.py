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
CHANNEL_IDS = [int(id.strip()) for id in os.getenv('CHANNEL_IDS', '').split(',') if id.strip()]
TARGET_USER_IDS = [int(id.strip()) for id in os.getenv('TARGET_USER_IDS', '').split(',') if id.strip()]
PUSHOVER_USER_KEY = os.getenv('PUSHOVER_USER_KEY')
PUSHOVER_API_TOKEN = os.getenv('PUSHOVER_API_TOKEN')

# Validate configuration
if not all([TOKEN, CHANNEL_IDS, TARGET_USER_IDS, PUSHOVER_USER_KEY, PUSHOVER_API_TOKEN]):
    print("Error: Please set all required environment variables in .env file")
    print("Required variables: DISCORD_TOKEN, CHANNEL_IDS, TARGET_USER_IDS, PUSHOVER_USER_KEY, PUSHOVER_API_TOKEN")
    sys.exit(1)

def send_pushover_notification(message, title=None, priority=0, sound="pushover", image_urls=None):
    """Send a notification via Pushover with optional image attachments."""
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
            
        # If we have image URLs, send a notification for each image
        if image_urls:
            for image_url in image_urls:
                try:
                    # Download the image
                    image_response = requests.get(image_url)
                    if image_response.status_code == 200:
                        # Create a copy of the data for this image
                        image_data = data.copy()
                        files = {'attachment': ('image.jpg', image_response.content)}
                        
                        # Send notification with image
                        r = requests.post("https://api.pushover.net/1/messages.json", 
                                        data=image_data, 
                                        files=files)
                        if r.status_code != 200:
                            print(f"Error sending image notification: {r.text}")
                    else:
                        print(f"Failed to download image: {image_url}")
                except Exception as e:
                    print(f"Error processing image {image_url}: {e}")
        else:
            # Only send a text message if there are no images
            r = requests.post("https://api.pushover.net/1/messages.json", data=data)
            if r.status_code != 200:
                print(f"Error sending notification: {r.text}")
    except Exception as e:
        print(f"Error sending notification: {e}")

class MessageMonitor(discord.Client):
    def __init__(self):
        super().__init__()
        self.target_channels = {}
        self.connected = False

    async def on_ready(self):
        """Called when the client is ready and connected to Discord."""
        print(f'Connected as {self.user} (ID: {self.user.id})')
        
        # Get all target channels
        for channel_id in CHANNEL_IDS:
            channel = self.get_channel(channel_id)
            if channel:
                self.target_channels[channel_id] = channel
                print(f"Monitoring channel: {channel.guild.name}/#{channel.name}")
            else:
                print(f"Warning: Could not find channel with ID {channel_id}")

        if not self.target_channels:
            print("Error: Could not find any of the specified channels")
            await self.close()
            return

        print(f"Filtering messages from user IDs: {', '.join(map(str, TARGET_USER_IDS))}")
        print("Waiting for messages...")
        self.connected = True

        # Send a test notification
        channels_str = ", ".join(f"{channel.guild.name}/#{channel.name}" for channel in self.target_channels.values())
        send_pushover_notification(
            f"Discord monitor started successfully!\nMonitoring channels: {channels_str}",
            title="Discord Monitor",
            priority=0
        )

    async def on_message(self, message):
        """Called when a message is sent in any visible channel."""
        try:
            # Check if message is in any target channel and from any target user
            if (message.channel.id in self.target_channels and 
                message.author.id in TARGET_USER_IDS):
                
                # Check if message contains prizepicks links, attachments, or embeds
                has_prize_links = any('prizepicks.onelink.me' in word for word in message.content.split())
                has_attachments = bool(message.attachments)
                has_embeds = bool(message.embeds)
                
                # Only proceed if message contains prizepicks links or media
                if has_prize_links or has_attachments or has_embeds:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    user_identifier = f"{message.author.display_name} (@{message.author.name})"
                    channel_identifier = f"{message.guild.name}/#{message.channel.name}"
                    console_msg = f"\n[{timestamp}] {channel_identifier} - {user_identifier}: {message.content}"
                    print(console_msg)
                    
                    # Prepare notification message
                    push_msg = f"{user_identifier}: {message.content}"
                    
                    # Collect image URLs from attachments
                    image_urls = []
                    if has_attachments:
                        for attachment in message.attachments:
                            if any(attachment.filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                                image_urls.append(attachment.url)
                            else:
                                # Non-image attachments are added as links to the message
                                push_msg += f"\n📎 {attachment.url}"
                    
                    # Add embeds to notification if any
                    if has_embeds:
                        for embed in message.embeds:
                            if embed.title:
                                embed_text = f"\n📌 {embed.title}"
                                if embed.description:
                                    embed_text += f": {embed.description}"
                                push_msg += embed_text
                                
                            # Check for image in embed
                            if embed.image:
                                image_urls.append(embed.image.url)
                    
                    # Send push notification with any images
                    send_pushover_notification(
                        push_msg,
                        title=f"Discord: {channel_identifier}",
                        priority=1,  # High priority for immediate delivery
                        sound="cosmic",  # Use a distinctive notification sound
                        image_urls=image_urls if image_urls else None
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