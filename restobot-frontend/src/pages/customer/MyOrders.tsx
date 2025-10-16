import React from 'react';
import { Container, Typography, Box } from '@mui/material';

const MyOrders: React.FC = () => {
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box>
        <Typography variant="h4" gutterBottom>
          Đơn hàng của tôi
        </Typography>
        <Typography variant="body1">
          Trang đơn hàng đang được phát triển...
        </Typography>
      </Box>
    </Container>
  );
};

export default MyOrders;