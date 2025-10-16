import React from 'react';
import { Container, Typography, Box } from '@mui/material';

const Menu: React.FC = () => {
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box>
        <Typography variant="h4" gutterBottom>
          Thực đơn
        </Typography>
        <Typography variant="body1">
          Trang thực đơn đang được phát triển...
        </Typography>
      </Box>
    </Container>
  );
};

export default Menu;