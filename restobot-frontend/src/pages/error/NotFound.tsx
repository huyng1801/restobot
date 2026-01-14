import React from 'react';
import { Box, Typography, Button, Container } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';

const NotFound: React.FC = () => {
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
        <ErrorOutlineIcon sx={{ fontSize: 80, color: 'error.main' }} />
        
        <Typography variant="h1" component="h1" color="error.main">
          404
        </Typography>
        
        <Typography variant="h4" component="h2" gutterBottom>
          Không tìm thấy trang
        </Typography>
        
        <Typography variant="body1" color="text.secondary" paragraph>
          Trang bạn đang tìm kiếm có thể đã bị xóa, đổi tên hoặc tạm thời không khả dụng.
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
            onClick={() => navigate(-1)}
          >
            Quay lại
          </Button>
        </Box>
      </Box>
    </Container>
  );
};

export default NotFound;