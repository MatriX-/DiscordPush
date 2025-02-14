export enum NotificationPriority {
  LOWEST = -2,
  LOW = -1,
  NORMAL = 0,
  HIGH = 1,
  EMERGENCY = 2,
}

export interface FilterConfig {
  keywords: string[];
  link_patterns: string[];
  image_types: string[];
  enabled: boolean;
}

export interface NotificationConfig {
  priority: NotificationPriority;
  sound: string;
  custom_message_template: string | null;
}

export interface Message {
  timestamp: string;
  channel: string;
  author: string;
  content: string;
  attachments: string[];
  embeds: Embed[];
}

export interface Embed {
  title?: string;
  description?: string;
}

export interface Channel {
  id: number;
  name: string;
}

export interface Status {
  connected: boolean;
  channels: Channel[];
}

export interface Config {
  channel_ids: number[];
  target_user_ids: number[];
  filters: FilterConfig;
  notifications: NotificationConfig;
} 