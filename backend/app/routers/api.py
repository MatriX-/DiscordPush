from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from ..models.config import Settings, FilterConfig, NotificationConfig
from ..discord.client import DiscordMonitor
from ..main import discord_client

router = APIRouter()

@router.get("/status")
async def get_status():
    """Get the current connection status of the Discord client."""
    if not discord_client:
        raise HTTPException(status_code=503, detail="Discord client not initialized")
    return {
        "connected": discord_client.connected,
        "channels": [
            {
                "id": channel_id,
                "name": f"{channel.guild.name} - #{channel.name}"
            }
            for channel_id, channel in discord_client.target_channels.items()
        ]
    }

@router.get("/messages")
async def get_messages():
    """Get recent message history."""
    if not discord_client:
        raise HTTPException(status_code=503, detail="Discord client not initialized")
    return discord_client.message_history

@router.get("/config")
async def get_config():
    """Get current configuration."""
    if not discord_client:
        raise HTTPException(status_code=503, detail="Discord client not initialized")
    return {
        "channel_ids": discord_client.settings.channel_ids,
        "target_user_ids": discord_client.settings.target_user_ids,
        "filters": discord_client.settings.filters,
        "notifications": discord_client.settings.notifications
    }

@router.put("/config/filters")
async def update_filters(filters: FilterConfig):
    """Update filter configuration."""
    if not discord_client:
        raise HTTPException(status_code=503, detail="Discord client not initialized")
    discord_client.settings.filters = filters
    return {"status": "success", "filters": filters}

@router.put("/config/notifications")
async def update_notifications(notifications: NotificationConfig):
    """Update notification configuration."""
    if not discord_client:
        raise HTTPException(status_code=503, detail="Discord client not initialized")
    discord_client.settings.notifications = notifications
    return {"status": "success", "notifications": notifications}

@router.put("/config/channels")
async def update_channels(channel_ids: List[int]):
    """Update monitored channel IDs."""
    if not discord_client:
        raise HTTPException(status_code=503, detail="Discord client not initialized")
    discord_client.settings.channel_ids = channel_ids
    # Reinitialize channels
    discord_client.target_channels.clear()
    for channel_id in channel_ids:
        channel = discord_client.get_channel(channel_id)
        if channel:
            discord_client.target_channels[channel_id] = channel
    return {"status": "success", "channel_ids": channel_ids}

@router.put("/config/users")
async def update_users(user_ids: List[int]):
    """Update target user IDs."""
    if not discord_client:
        raise HTTPException(status_code=503, detail="Discord client not initialized")
    discord_client.settings.target_user_ids = user_ids
    return {"status": "success", "user_ids": user_ids} 