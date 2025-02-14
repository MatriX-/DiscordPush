import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Box, Container } from '@mui/material';
import Navigation from './components/Navigation';
import Dashboard from './components/Dashboard';
import ConfigurationPage from './components/ConfigurationPage';
import MessageHistory from './components/MessageHistory';

const App: React.FC = () => {
  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: 'background.default' }}>
      <Navigation />
      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <Container maxWidth="lg" sx={{ mt: 8 }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/config" element={<ConfigurationPage />} />
            <Route path="/history" element={<MessageHistory />} />
          </Routes>
        </Container>
      </Box>
    </Box>
  );
};

export default App;
