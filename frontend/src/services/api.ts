import axios from 'axios';
import { FilterConfig, NotificationConfig } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:7777/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getStatus = async () => {
  const response = await api.get('/status');
  return response.data;
};

export const getMessages = async () => {
  const response = await api.get('/messages');
  return response.data;
};

export const getConfig = async () => {
  const response = await api.get('/config');
  return response.data;
};

export const updateFilters = async (filters: FilterConfig) => {
  const response = await api.put('/config/filters', filters);
  return response.data;
};

export const updateNotifications = async (notifications: NotificationConfig) => {
  const response = await api.put('/config/notifications', notifications);
  return response.data;
};

export const updateChannels = async (channelIds: number[]) => {
  const response = await api.put('/config/channels', channelIds);
  return response.data;
};

export const updateUsers = async (userIds: number[]) => {
  const response = await api.put('/config/users', userIds);
  return response.data;
}; 