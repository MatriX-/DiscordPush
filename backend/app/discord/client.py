import discord
from datetime import datetime
from typing import Dict, Optional, List
from ..models.config import Settings, FilterConfig
from ..services.pushover import send_pushover_notification

class DiscordMonitor(discord.Client):
    """Discord client for monitoring specific channels and users with configurable filters."""
    
    def __init__(self, settings: Settings):
        """Initialize the message monitor with settings."""
        super().__init__()
        self.settings = settings
        self.target_channels: Dict[int, discord.TextChannel] = {}
        self.connected = False
        self._message_history: List[Dict] = []  # Store recent messages for dashboard

    @property
    def message_history(self) -> List[Dict]:
        """Get recent message history for the dashboard."""
        return self._message_history[-100:]  # Keep last 100 messages

    def _add_to_history(self, message_data: Dict):
        """Add a message to history with size limit."""
        self._message_history.append(message_data)
        if len(self._message_history) > 100:
            self._message_history.pop(0)

    async def start(self):
        """Start the Discord client."""
        await super().start(self.settings.discord_token)

    async def on_ready(self):
        """Handler for when the client successfully connects to Discord."""
        print(f'Connected as {self.user} (ID: {self.user.id})')
        
        # Initialize monitoring for all configured channels
        for channel_id in self.settings.channel_ids:
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

        print(f"Filtering messages from user IDs: {', '.join(map(str, self.settings.target_user_ids))}")
        print("Waiting for messages...")
        self.connected = True

        # Send startup notification
        channels_str = ", ".join(f"{channel.guild.name} - #{channel.name}" 
                               for channel in self.target_channels.values())
        await self._send_notification(
            f"Discord monitor started successfully!\nMonitoring channels: {channels_str}",
            title="Discord Monitor"
        )

    def _check_filters(self, message: discord.Message) -> bool:
        """Check if message matches current filter configuration."""
        filters = self.settings.filters
        
        if not filters.enabled:
            return True
            
        # Check keywords
        if filters.keywords and any(keyword.lower() in message.content.lower() 
                                  for keyword in filters.keywords):
            return True
            
        # Check link patterns
        if filters.link_patterns and any(pattern in word 
                                       for pattern in filters.link_patterns 
                                       for word in message.content.split()):
            return True
            
        # Check attachments
        if message.attachments and filters.image_types:
            if any(any(attachment.filename.lower().endswith(f".{ext}") 
                      for ext in filters.image_types)
                  for attachment in message.attachments):
                return True
                
        # Check embeds
        if message.embeds and (filters.link_patterns or filters.image_types):
            return True
            
        return False

    async def _send_notification(self, message: str, title: Optional[str] = None, 
                               image_urls: Optional[List[str]] = None):
        """Send notification using current notification configuration."""
        config = self.settings.notifications
        await send_pushover_notification(
            message=message,
            title=title,
            priority=config.priority,
            sound=config.sound,
            image_urls=image_urls,
            user_key=self.settings.pushover_user_key,
            api_token=self.settings.pushover_api_token
        )

    async def on_message(self, message: discord.Message):
        """Handler for new messages in any visible channel."""
        try:
            # Verify message is from monitored channel and user
            if (message.channel.id in self.target_channels and 
                message.author.id in self.settings.target_user_ids):
                
                # Apply filters
                if not self._check_filters(message):
                    return
                
                # Process message
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                user_identifier = f"{message.author.display_name} (@{message.author.name})"
                channel_identifier = f"{message.guild.name} - #{message.channel.name}"
                
                # Store message in history
                message_data = {
                    "timestamp": timestamp,
                    "channel": channel_identifier,
                    "author": user_identifier,
                    "content": message.content,
                    "attachments": [a.url for a in message.attachments],
                    "embeds": [{"title": e.title, "description": e.description} 
                              for e in message.embeds]
                }
                self._add_to_history(message_data)
                
                # Build notification
                push_msg = f"{user_identifier}: {message.content}"
                image_urls = []
                
                # Process attachments
                for attachment in message.attachments:
                    if any(attachment.filename.lower().endswith(ext) 
                          for ext in self.settings.filters.image_types):
                        image_urls.append(attachment.url)
                    else:
                        push_msg += f"\n📎 {attachment.url}"
                
                # Process embeds
                for embed in message.embeds:
                    if embed.title:
                        embed_text = f"\n📌 {embed.title}"
                        if embed.description:
                            embed_text += f": {embed.description}"
                        push_msg += embed_text
                        
                    if embed.image:
                        image_urls.append(embed.image.url)
                
                # Send notification
                await self._send_notification(
                    push_msg,
                    title=f"Discord: {channel_identifier}",
                    image_urls=image_urls if image_urls else None
                )
        
        except Exception as e:
            print(f"Error processing message: {e}")
            await self._send_notification(
                f"Error processing message: {e}",
                title="Discord Monitor Error"
            )

    async def on_error(self, event, *args, **kwargs):
        """Handler for client errors."""
        error_msg = f"Error in {event}: {args[0]}"
        print(error_msg)
        await self._send_notification(
            error_msg,
            title="Discord Monitor Error"
        )

    async def on_disconnect(self):
        """Handler for Discord disconnection events."""
        self.connected = False
        disconnect_msg = "Disconnected from Discord. Attempting to reconnect..."
        print(disconnect_msg)
        await self._send_notification(
            disconnect_msg,
            title="Discord Monitor Status"
        ) 