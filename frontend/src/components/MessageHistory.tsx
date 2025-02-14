import React from 'react';
import { useQuery } from 'react-query';
import {
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  Box,
  CircularProgress,
  Alert,
  Chip,
  Divider,
} from '@mui/material';
import { AttachFile, Image } from '@mui/icons-material';
import { getMessages } from '../services/api';

const MessageHistory: React.FC = () => {
  const { data: messages, isLoading, error } = useQuery('messages', getMessages, {
    refetchInterval: 5000,
  });

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
        Error loading message history. Please check your connection and try again.
      </Alert>
    );
  }

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Message History
      </Typography>
      <List>
        {messages?.map((message, index) => (
          <React.Fragment key={index}>
            <ListItem alignItems="flex-start">
              <ListItemText
                primary={
                  <Box display="flex" alignItems="center" gap={1}>
                    <Typography component="span" variant="body1">
                      {message.content}
                    </Typography>
                    {message.attachments.length > 0 && (
                      <Chip
                        icon={<AttachFile />}
                        label={`${message.attachments.length} attachment(s)`}
                        size="small"
                        variant="outlined"
                      />
                    )}
                    {message.embeds.length > 0 && (
                      <Chip
                        icon={<Image />}
                        label={`${message.embeds.length} embed(s)`}
                        size="small"
                        variant="outlined"
                      />
                    )}
                  </Box>
                }
                secondary={
                  <React.Fragment>
                    <Typography
                      component="span"
                      variant="body2"
                      color="text.primary"
                    >
                      {message.author}
                    </Typography>
                    {" — "}
                    {message.timestamp}
                    {message.attachments.length > 0 && (
                      <Box sx={{ mt: 1 }}>
                        {message.attachments.map((url, i) => (
                          <Box
                            key={i}
                            component="a"
                            href={url}
                            target="_blank"
                            rel="noopener noreferrer"
                            sx={{
                              display: 'block',
                              color: 'primary.main',
                              textDecoration: 'none',
                              '&:hover': {
                                textDecoration: 'underline',
                              },
                            }}
                          >
                            Attachment {i + 1}
                          </Box>
                        ))}
                      </Box>
                    )}
                    {message.embeds.length > 0 && (
                      <Box sx={{ mt: 1 }}>
                        {message.embeds.map((embed, i) => (
                          <Box key={i}>
                            {embed.title && (
                              <Typography variant="subtitle2">
                                {embed.title}
                              </Typography>
                            )}
                            {embed.description && (
                              <Typography variant="body2">
                                {embed.description}
                              </Typography>
                            )}
                          </Box>
                        ))}
                      </Box>
                    )}
                  </React.Fragment>
                }
              />
            </ListItem>
            {index < messages.length - 1 && <Divider />}
          </React.Fragment>
        ))}
      </List>
    </Paper>
  );
};

export default MessageHistory; 