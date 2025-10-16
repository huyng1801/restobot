import React, { useState, useEffect } from 'react';
import { Box, Grid, Card, CardContent, Typography, Button, CircularProgress, Alert } from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  ShoppingCart as OrdersIcon,
  TableBar as TablesIcon,
  People as UsersIcon,
  AttachMoney as RevenueIcon,
  Schedule as PendingIcon,
  CheckCircle as CompletedIcon,
} from '@mui/icons-material';
import AdminLayout from '../../components/admin/AdminLayout';
import { useNavigate } from 'react-router-dom';
import { orderService } from '../../services/adminService';
import { DailySummary } from '../../types';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [summary, setSummary] = useState<DailySummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadSummary();
  }, []);

  const loadSummary = async () => {
    try {
      setLoading(true);
      const response = await orderService.getDailySummary();
      setSummary(response);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Lỗi tải dữ liệu');
    } finally {
      setLoading(false);
    }
  };

  const stats = [
    {
      title: 'Tổng đơn hàng',
      value: summary ? summary.total_orders : '0',
      icon: <OrdersIcon sx={{ fontSize: 40 }} />,
      color: '#2196f3',
      action: () => navigate('/admin/orders'),
    },
    {
      title: 'Doanh thu hôm nay',
      value: summary ? `${summary.total_revenue.toLocaleString()}đ` : '0đ',
      icon: <RevenueIcon sx={{ fontSize: 40 }} />,
      color: '#4caf50',
      action: () => navigate('/admin/orders'),
    },
    {
      title: 'Đơn hàng chờ',
      value: summary ? summary.pending_orders : '0',
      icon: <PendingIcon sx={{ fontSize: 40 }} />,
      color: '#ff9800',
      action: () => navigate('/admin/orders'),
    },
    {
      title: 'Đơn hàng hoàn thành',
      value: summary ? summary.completed_orders : '0',
      icon: <CompletedIcon sx={{ fontSize: 40 }} />,
      color: '#d32f2f',
      action: () => navigate('/admin/orders'),
    },
  ];

  return (
    <AdminLayout>
      <Box>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
          Bảng Điều Khiển
        </Typography>

        {error && <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>{error}</Alert>}

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '200px' }}>
            <CircularProgress />
          </Box>
        ) : (
          /* Stats Grid */
          <Grid container spacing={3} sx={{ mb: 4 }}>
            {stats.map((stat, index) => (
              <Grid item xs={12} sm={6} md={3} key={index}>
                <Card
                  onClick={stat.action}
                  sx={{
                    cursor: 'pointer',
                    transition: 'all 0.3s',
                    '&:hover': {
                      boxShadow: 6,
                      transform: 'translateY(-4px)',
                    },
                  }}
                >
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Box
                      sx={{
                        bgcolor: `${stat.color}20`,
                        borderRadius: 2,
                        p: 1.5,
                        display: 'flex',
                        color: stat.color,
                      }}
                    >
                      {stat.icon}
                    </Box>
                    <Box sx={{ flex: 1 }}>
                      <Typography color="textSecondary" variant="body2">
                        {stat.title}
                      </Typography>
                      <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                        {stat.value}
                      </Typography>
                    </Box>
                  </Box>
                  <Button
                    size="small"
                    sx={{ mt: 2, color: stat.color }}
                    onClick={stat.action}
                  >
                    Xem chi tiết →
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
        )}

        {/* Recent Activity */}
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2 }}>
                  Đơn Hàng Gần Đây
                </Typography>
                <Typography color="textSecondary" variant="body2">
                  Tính năng đang được phát triển...
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2 }}>
                  Đặt Bàn Gần Đây
                </Typography>
                <Typography color="textSecondary" variant="body2">
                  Tính năng đang được phát triển...
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </AdminLayout>
  );
};

export default Dashboard;