import React from 'react';
import { Container, Typography, Box } from '@mui/material';

const MyReservations: React.FC = () => {
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box>
        <Typography variant="h4" gutterBottom>
          Đặt bàn của tôi
        </Typography>
        <Typography variant="body1">
          Trang đặt bàn đang được phát triển...
        </Typography>
      </Box>
    </Container>
  );
};

export default MyReservations;