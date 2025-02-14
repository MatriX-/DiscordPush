import os
import sys
import asyncio
import discord
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Parse and validate configuration from environment variables
# Converting comma-separated string lists into integer arrays for channel and user IDs
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_IDS = [int(id.strip()) for id in os.getenv('CHANNEL_IDS', '').split(',') if id.strip()]
TARGET_USER_IDS = [int(id.strip()) for id in os.getenv('TARGET_USER_IDS', '').split(',') if id.strip()]
PUSHOVER_USER_KEY = os.getenv('PUSHOVER_USER_KEY')
PUSHOVER_API_TOKEN = os.getenv('PUSHOVER_API_TOKEN')

# Validate that all required configuration is present
# Exit early if any required variables are missing to prevent runtime errors
if not all([TOKEN, CHANNEL_IDS, TARGET_USER_IDS, PUSHOVER_USER_KEY, PUSHOVER_API_TOKEN]):
    print("Error: Please set all required environment variables in .env file")
    print("Required variables: DISCORD_TOKEN, CHANNEL_IDS, TARGET_USER_IDS, PUSHOVER_USER_KEY, PUSHOVER_API_TOKEN")
    sys.exit(1)

def send_pushover_notification(message, title=None, priority=0, sound="pushover", image_urls=None):
    """Send a notification via Pushover with optional image attachments.
    
    Args:
        message (str): The main notification message
        title (str, optional): Title for the notification. Defaults to None.
        priority (int, optional): Message priority (-2 to 2). Defaults to 0.
        sound (str, optional): Notification sound to play. Defaults to "pushover".
        image_urls (list, optional): List of image URLs to attach. Defaults to None.
    
    The function handles both text-only notifications and notifications with images:
    - For text-only notifications, sends a single Pushover API request
    - For notifications with images, sends multiple requests (one per image)
    - Each image is downloaded and attached to its own notification
    - Errors are caught and logged but don't stop execution
    """
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
            
        # Handle image attachments if present
        if image_urls:
            for image_url in image_urls:
                try:
                    # Download each image
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
            # Send text-only notification
            r = requests.post("https://api.pushover.net/1/messages.json", data=data)
            if r.status_code != 200:
                print(f"Error sending notification: {r.text}")
    except Exception as e:
        print(f"Error sending notification: {e}")

class MessageMonitor(discord.Client):
    """Discord client for monitoring specific channels and users.
    
    This client watches configured channels for messages from specific users
    and forwards relevant messages (containing links or media) to Pushover.
    """
    
    def __init__(self):
        """Initialize the message monitor.
        
        Sets up:
        - Parent discord.Client
        - Dictionary to store target channels
        - Connection status tracking
        """
        super().__init__()
        self.target_channels = {}  # Maps channel IDs to channel objects
        self.connected = False     # Tracks connection status

    async def on_ready(self):
        """Handler for when the client successfully connects to Discord.
        
        This method:
        1. Initializes monitoring for all configured channels
        2. Validates channel access
        3. Sends a startup notification via Pushover
        4. Exits if no valid channels are found
        """
        print(f'Connected as {self.user} (ID: {self.user.id})')
        
        # Initialize monitoring for all configured channels
        for channel_id in CHANNEL_IDS:
            channel = self.get_channel(channel_id)
            if channel:
                self.target_channels[channel_id] = channel
                print(f"Monitoring channel: {channel.guild.name} - #{channel.name}")
            else:
                print(f"Warning: Could not find channel with ID {channel_id}")

        if not self.target_channels:
            print("Error: Could not find any of the specified channels")
            await self.close()
            return

        print(f"Filtering messages from user IDs: {', '.join(map(str, TARGET_USER_IDS))}")
        print("Waiting for messages...")
        self.connected = True

        # Send startup notification
        channels_str = ", ".join(f"{channel.guild.name} - #{channel.name}" for channel in self.target_channels.values())
        send_pushover_notification(
            f"Discord monitor started successfully!\nMonitoring channels: {channels_str}",
            title="Discord Monitor",
            priority=0
        )

    async def on_message(self, message):
        """Handler for new messages in any visible channel.
        
        This method processes each message by:
        1. Checking if it's from a monitored channel and user
        2. Looking for prizepicks links or media content
        3. Formatting and sending notifications for relevant messages
        4. Handling any attachments or embeds in the message
        
        Args:
            message: The Discord message object to process
        """
        try:
            # Verify message is from monitored channel and user
            if (message.channel.id in self.target_channels and 
                message.author.id in TARGET_USER_IDS):
                
                # Check for relevant content
                has_prize_links = any('prizepicks.onelink.me' in word for word in message.content.split())
                has_attachments = bool(message.attachments)
                has_embeds = bool(message.embeds)
                
                # Process relevant messages
                if has_prize_links or has_attachments or has_embeds:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    user_identifier = f"{message.author.display_name} (@{message.author.name})"
                    channel_identifier = f"{message.guild.name} - #{message.channel.name}"
                    console_msg = f"\n[{timestamp}] {channel_identifier} - {user_identifier}: {message.content}"
                    print(console_msg)
                    
                    # Build notification message
                    push_msg = f"{user_identifier}: {message.content}"
                    
                    # Process attachments
                    image_urls = []
                    if has_attachments:
                        for attachment in message.attachments:
                            if any(attachment.filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                                image_urls.append(attachment.url)
                            else:
                                # Add non-image attachments as links
                                push_msg += f"\n📎 {attachment.url}"
                    
                    # Process embeds
                    if has_embeds:
                        for embed in message.embeds:
                            if embed.title:
                                embed_text = f"\n📌 {embed.title}"
                                if embed.description:
                                    embed_text += f": {embed.description}"
                                push_msg += embed_text
                                
                            if embed.image:
                                image_urls.append(embed.image.url)
                    
                    # Send the notification
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
        """Handler for client errors.
        
        Logs errors and sends notifications when something goes wrong.
        
        Args:
            event: The event that triggered the error
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """
        error_msg = f"Error in {event}: {sys.exc_info()[1]}"
        print(error_msg)
        send_pushover_notification(
            error_msg,
            title="Discord Monitor Error",
            priority=1,
            sound="falling"
        )

    async def on_disconnect(self):
        """Handler for Discord disconnection events.
        
        Updates connection status and sends notification when disconnected.
        The client will automatically attempt to reconnect.
        """
        self.connected = False
        disconnect_msg = "Disconnected from Discord. Attempting to reconnect..."
        print(disconnect_msg)
        send_pushover_notification(
            disconnect_msg,
            title="Discord Monitor Status",
            priority=0
        )

def main():
    """Main entry point for the Discord monitor.
    
    This function:
    1. Creates and initializes the MessageMonitor client
    2. Handles startup errors (invalid token, etc.)
    3. Ensures clean shutdown in case of errors
    """
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