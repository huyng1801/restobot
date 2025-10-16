import React from 'react';
import { Container, Typography, Box } from '@mui/material';

const Profile: React.FC = () => {
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box>
        <Typography variant="h4" gutterBottom>
          Hồ sơ cá nhân
        </Typography>
        <Typography variant="body1">
          Trang hồ sơ đang được phát triển...
        </Typography>
      </Box>
    </Container>
  );
};

export default Profile;