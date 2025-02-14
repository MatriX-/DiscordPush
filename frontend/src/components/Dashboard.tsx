import React from 'react';
import { useQuery } from 'react-query';
import {
  Grid,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  Chip,
  Box,
  CircularProgress,
  Alert,
} from '@mui/material';
import { CheckCircle, Error } from '@mui/icons-material';
import { getStatus, getMessages } from '../services/api';

const Dashboard: React.FC = () => {
  const { data: status, isLoading: statusLoading, error: statusError } = useQuery(
    'status',
    getStatus,
    { refetchInterval: 5000 }
  );

  const { data: messages, isLoading: messagesLoading, error: messagesError } = useQuery(
    'messages',
    getMessages,
    { refetchInterval: 5000 }
  );

  if (statusLoading || messagesLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
        <CircularProgress />
      </Box>
    );
  }

  if (statusError || messagesError) {
    return (
      <Alert severity="error">
        Error loading dashboard data. Please check your connection and try again.
      </Alert>
    );
  }

  return (
    <Grid container spacing={3}>
      {/* Status Section */}
      <Grid item xs={12}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            System Status
          </Typography>
          <Box display="flex" alignItems="center" gap={2}>
            {status?.connected ? (
              <Chip
                icon={<CheckCircle />}
                label="Connected"
                color="success"
                variant="outlined"
              />
            ) : (
              <Chip
                icon={<Error />}
                label="Disconnected"
                color="error"
                variant="outlined"
              />
            )}
          </Box>
        </Paper>
      </Grid>

      {/* Monitored Channels */}
      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Monitored Channels
          </Typography>
          <List>
            {status?.channels.map((channel) => (
              <ListItem key={channel.id}>
                <ListItemText primary={channel.name} />
              </ListItem>
            ))}
          </List>
        </Paper>
      </Grid>

      {/* Recent Activity */}
      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Recent Activity
          </Typography>
          <List>
            {messages?.slice(0, 5).map((message, index) => (
              <ListItem key={index}>
                <ListItemText
                  primary={message.content}
                  secondary={`${message.author} - ${message.timestamp}`}
                />
              </ListItem>
            ))}
          </List>
        </Paper>
      </Grid>
    </Grid>
  );
};

export default Dashboard; 