import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import {
  Grid,
  Paper,
  Typography,
  TextField,
  Button,
  Switch,
  FormControlLabel,
  Chip,
  Box,
  Alert,
  CircularProgress,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import { getConfig, updateFilters, updateNotifications } from '../services/api';
import { FilterConfig, NotificationConfig, NotificationPriority } from '../types';

const ConfigurationPage: React.FC = () => {
  const queryClient = useQueryClient();
  const { data: config, isLoading, error } = useQuery('config', getConfig);

  const [filters, setFilters] = useState<FilterConfig>({
    keywords: [],
    link_patterns: [],
    image_types: ['jpg', 'jpeg', 'png', 'gif'],
    enabled: true,
  });

  const [notifications, setNotifications] = useState<NotificationConfig>({
    priority: NotificationPriority.NORMAL,
    sound: 'pushover',
    custom_message_template: null,
  });

  // Update state when data is loaded
  React.useEffect(() => {
    if (config) {
      setFilters(config.filters);
      setNotifications(config.notifications);
    }
  }, [config]);

  const filtersMutation = useMutation(updateFilters, {
    onSuccess: () => {
      queryClient.invalidateQueries('config');
    },
  });

  const notificationsMutation = useMutation(updateNotifications, {
    onSuccess: () => {
      queryClient.invalidateQueries('config');
    },
  });

  const handleKeywordAdd = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter' && event.currentTarget.value) {
      setFilters({
        ...filters,
        keywords: [...filters.keywords, event.currentTarget.value],
      });
      event.currentTarget.value = '';
    }
  };

  const handleKeywordDelete = (keyword: string) => {
    setFilters({
      ...filters,
      keywords: filters.keywords.filter((k) => k !== keyword),
    });
  };

  const handleLinkPatternAdd = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter' && event.currentTarget.value) {
      setFilters({
        ...filters,
        link_patterns: [...filters.link_patterns, event.currentTarget.value],
      });
      event.currentTarget.value = '';
    }
  };

  const handleLinkPatternDelete = (pattern: string) => {
    setFilters({
      ...filters,
      link_patterns: filters.link_patterns.filter((p) => p !== pattern),
    });
  };

  const handleSaveFilters = () => {
    filtersMutation.mutate(filters);
  };

  const handleSaveNotifications = () => {
    notificationsMutation.mutate(notifications);
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error">
        Error loading configuration. Please check your connection and try again.
      </Alert>
    );
  }

  return (
    <Grid container spacing={3}>
      {/* Filter Configuration */}
      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Filter Configuration
          </Typography>
          
          <FormControlLabel
            control={
              <Switch
                checked={filters.enabled}
                onChange={(e) => setFilters({ ...filters, enabled: e.target.checked })}
              />
            }
            label="Enable Filters"
          />

          <Box sx={{ mt: 2 }}>
            <TextField
              fullWidth
              label="Add Keyword"
              placeholder="Press Enter to add"
              onKeyPress={handleKeywordAdd}
            />
            <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {filters.keywords.map((keyword) => (
                <Chip
                  key={keyword}
                  label={keyword}
                  onDelete={() => handleKeywordDelete(keyword)}
                />
              ))}
            </Box>
          </Box>

          <Box sx={{ mt: 2 }}>
            <TextField
              fullWidth
              label="Add Link Pattern"
              placeholder="Press Enter to add"
              onKeyPress={handleLinkPatternAdd}
            />
            <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {filters.link_patterns.map((pattern) => (
                <Chip
                  key={pattern}
                  label={pattern}
                  onDelete={() => handleLinkPatternDelete(pattern)}
                />
              ))}
            </Box>
          </Box>

          <Button
            variant="contained"
            color="primary"
            onClick={handleSaveFilters}
            sx={{ mt: 2 }}
          >
            Save Filters
          </Button>
        </Paper>
      </Grid>

      {/* Notification Configuration */}
      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Notification Configuration
          </Typography>

          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Priority</InputLabel>
            <Select
              value={notifications.priority}
              label="Priority"
              onChange={(e) => setNotifications({
                ...notifications,
                priority: e.target.value as NotificationPriority,
              })}
            >
              <MenuItem value={NotificationPriority.LOWEST}>Lowest</MenuItem>
              <MenuItem value={NotificationPriority.LOW}>Low</MenuItem>
              <MenuItem value={NotificationPriority.NORMAL}>Normal</MenuItem>
              <MenuItem value={NotificationPriority.HIGH}>High</MenuItem>
              <MenuItem value={NotificationPriority.EMERGENCY}>Emergency</MenuItem>
            </Select>
          </FormControl>

          <TextField
            fullWidth
            label="Sound"
            value={notifications.sound}
            onChange={(e) => setNotifications({
              ...notifications,
              sound: e.target.value,
            })}
            sx={{ mt: 2 }}
          />

          <TextField
            fullWidth
            label="Custom Message Template"
            value={notifications.custom_message_template || ''}
            onChange={(e) => setNotifications({
              ...notifications,
              custom_message_template: e.target.value || null,
            })}
            multiline
            rows={3}
            sx={{ mt: 2 }}
          />

          <Button
            variant="contained"
            color="primary"
            onClick={handleSaveNotifications}
            sx={{ mt: 2 }}
          >
            Save Notification Settings
          </Button>
        </Paper>
      </Grid>
    </Grid>
  );
};

export default ConfigurationPage; 