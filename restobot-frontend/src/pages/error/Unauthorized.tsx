import React from 'react';
import { Box, Typography, Button, Container } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import LockIcon from '@mui/icons-material/Lock';

const Unauthorized: React.FC = () => {
  const navigate = useNavigate();

  return (
    <Container maxWidth="sm">
      <Box
        display="flex"
        flexDirection="column"
        alignItems="center"
        justifyContent="center"
        minHeight="100vh"
        textAlign="center"
        gap={3}
      >
        <LockIcon sx={{ fontSize: 80, color: 'warning.main' }} />
        
        <Typography variant="h1" component="h1" color="warning.main">
          403
        </Typography>
        
        <Typography variant="h4" component="h2" gutterBottom>
          Không có quyền truy cập
        </Typography>
        
        <Typography variant="body1" color="text.secondary" paragraph>
          Bạn không có quyền truy cập vào trang này. Vui lòng liên hệ quản trị viên nếu bạn cho rằng đây là lỗi.
        </Typography>
        
        <Box display="flex" gap={2}>
          <Button
            variant="contained"
            color="primary"
            onClick={() => navigate('/')}
          >
            Về trang chủ
          </Button>
          
          <Button
            variant="outlined"
            color="primary"
            onClick={() => navigate('/login')}
          >
            Đăng nhập
          </Button>
        </Box>
      </Box>
    </Container>
  );
};

export default Unauthorized;