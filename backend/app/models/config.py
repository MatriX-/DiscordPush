from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from typing import List, Optional, Dict
from enum import Enum

class NotificationPriority(str, Enum):
    LOWEST = -2
    LOW = -1
    NORMAL = 0
    HIGH = 1
    EMERGENCY = 2

class FilterConfig(BaseModel):
    keywords: List[str] = Field(default_factory=list)
    link_patterns: List[str] = Field(default_factory=list)
    image_types: List[str] = Field(default=['jpg', 'jpeg', 'png', 'gif'])
    enabled: bool = True

class NotificationConfig(BaseModel):
    priority: NotificationPriority = NotificationPriority.NORMAL
    sound: str = "pushover"
    custom_message_template: Optional[str] = None

class Settings(BaseSettings):
    discord_token: str
    channel_ids: List[int]
    target_user_ids: List[int]
    pushover_user_key: str
    pushover_api_token: str
    filters: FilterConfig = Field(default_factory=FilterConfig)
    notifications: NotificationConfig = Field(default_factory=NotificationConfig)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8" 