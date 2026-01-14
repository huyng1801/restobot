import React, { useState, useEffect } from 'react';
import { 
  Box, Grid, Card, CardContent, Typography, Button, CircularProgress, Alert,
  List, ListItem, ListItemText, ListItemAvatar, Avatar, Chip,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  LinearProgress
} from '@mui/material';
import {
  ShoppingCart as OrdersIcon,
  TableBar as TablesIcon,
  AttachMoney as RevenueIcon,
  Schedule as PendingIcon,
  CheckCircle as CompletedIcon,
  Restaurant as MenuIcon,
  EventSeat as ReservationIcon,
  StarBorder as PopularIcon,
  AccessTime as RecentIcon,
  PersonAdd as CustomerIcon,
  Group as StaffIcon,
} from '@mui/icons-material';
import AdminLayout from '../../components/admin/AdminLayout';
import { useNavigate } from 'react-router-dom';
import { orderService } from '../../services/admin';
import { DashboardStats } from '../../types/adminTypes';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [dashboardStats, setDashboardStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardStats();
  }, []);

  const loadDashboardStats = async () => {
    try {
      setLoading(true);
      const response = await orderService.getDashboardStats();
      setDashboardStats(response);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Lỗi tải dữ liệu');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return '#ff9800';
      case 'confirmed': return '#2196f3';  
      case 'preparing': return '#9c27b0';
      case 'ready': return '#4caf50';
      case 'completed': return '#4caf50';
      case 'cancelled': return '#f44336';
      default: return '#757575';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'pending': return 'Chờ xử lý';
      case 'confirmed': return 'Đã xác nhận';
      case 'preparing': return 'Đang chuẩn bị';
      case 'ready': return 'Sẵn sàng';
      case 'completed': return 'Hoàn thành';
      case 'cancelled': return 'Đã hủy';
      default: return status;
    }
  };

  const statsCards = [
    {
      title: 'Tổng đơn hàng',
      value: dashboardStats ? dashboardStats.total_orders : '0',
      icon: <OrdersIcon sx={{ fontSize: 40 }} />,
      color: '#2196f3',
      action: () => navigate('/admin/orders'),
    },
    {
      title: 'Doanh thu hôm nay', 
      value: dashboardStats ? `${dashboardStats.total_revenue.toLocaleString()}đ` : '0đ',
      icon: <RevenueIcon sx={{ fontSize: 40 }} />,
      color: '#4caf50',
      action: () => navigate('/admin/orders'),
    },
    {
      title: 'Tổng khách hàng',
      value: dashboardStats ? dashboardStats.total_customers : '0',
      icon: <CustomerIcon sx={{ fontSize: 40 }} />,
      color: '#9c27b0',
      action: () => navigate('/admin/users'),
    },
    {
      title: 'Tổng nhân viên',
      value: dashboardStats ? dashboardStats.total_staff : '0', 
      icon: <StaffIcon sx={{ fontSize: 40 }} />,
      color: '#ff5722',
      action: () => navigate('/admin/users'),
    },
    {
      title: 'Tổng bàn',
      value: dashboardStats ? dashboardStats.total_tables : '0',
      icon: <TablesIcon sx={{ fontSize: 40 }} />,
      color: '#607d8b',
      action: () => navigate('/admin/tables'),
    },
    {
      title: 'Bàn trống',
      value: dashboardStats ? dashboardStats.available_tables : '0',
      icon: <CompletedIcon sx={{ fontSize: 40 }} />,
      color: '#4caf50',
      action: () => navigate('/admin/tables'),
    },
    {
      title: 'Tổng món ăn',
      value: dashboardStats ? dashboardStats.total_menu_items : '0',
      icon: <MenuIcon sx={{ fontSize: 40 }} />,
      color: '#e91e63',
      action: () => navigate('/admin/menu'),
    },
    {
      title: 'Tổng đặt bàn',
      value: dashboardStats ? dashboardStats.total_reservations : '0',
      icon: <ReservationIcon sx={{ fontSize: 40 }} />,
      color: '#795548',
      action: () => navigate('/admin/reservations'),
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
          <>
            {/* Stats Grid */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
              {statsCards.map((stat, index) => (
                <Grid item xs={12} sm={6} lg={3} key={index}>
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

          {/* Order Status Summary */}
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                    <PendingIcon color="warning" />
                    Trạng Thái Đơn Hàng
                  </Typography>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="textSecondary">
                      Đơn hàng chờ: {dashboardStats?.pending_orders || 0}
                    </Typography>
                    <LinearProgress 
                      variant="determinate" 
                      value={dashboardStats ? (dashboardStats.pending_orders / Math.max(dashboardStats.total_orders, 1)) * 100 : 0}
                      sx={{ mt: 1, mb: 1 }}
                      color="warning"
                    />
                  </Box>
                  <Box>
                    <Typography variant="body2" color="textSecondary">
                      Đơn hàng hoàn thành: {dashboardStats?.completed_orders || 0}
                    </Typography>
                    <LinearProgress 
                      variant="determinate"
                      value={dashboardStats ? (dashboardStats.completed_orders / Math.max(dashboardStats.total_orders, 1)) * 100 : 0}
                      sx={{ mt: 1 }}
                      color="success"
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                    <TablesIcon color="primary" />
                    Trạng Thái Bàn
                  </Typography>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="textSecondary">
                      Bàn trống: {dashboardStats?.available_tables || 0}
                    </Typography>
                    <LinearProgress 
                      variant="determinate"
                      value={dashboardStats ? (dashboardStats.available_tables / Math.max(dashboardStats.total_tables, 1)) * 100 : 0}
                      sx={{ mt: 1, mb: 1 }}
                      color="success"
                    />
                  </Box>
                  <Box>
                    <Typography variant="body2" color="textSecondary">
                      Bàn đã đặt: {dashboardStats?.occupied_tables || 0}
                    </Typography>
                    <LinearProgress 
                      variant="determinate"
                      value={dashboardStats ? (dashboardStats.occupied_tables / Math.max(dashboardStats.total_tables, 1)) * 100 : 0}
                      sx={{ mt: 1 }}
                      color="error"
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                    <ReservationIcon color="secondary" />
                    Đặt Bàn
                  </Typography>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="textSecondary">
                      Chờ xác nhận: {dashboardStats?.pending_reservations || 0}
                    </Typography>
                    <LinearProgress 
                      variant="determinate"
                      value={dashboardStats ? (dashboardStats.pending_reservations / Math.max(dashboardStats.total_reservations, 1)) * 100 : 0}
                      sx={{ mt: 1, mb: 1 }}
                      color="warning"
                    />
                  </Box>
                  <Box>
                    <Typography variant="body2" color="textSecondary">
                      Đã xác nhận: {dashboardStats?.confirmed_reservations || 0}
                    </Typography>
                    <LinearProgress 
                      variant="determinate"
                      value={dashboardStats ? (dashboardStats.confirmed_reservations / Math.max(dashboardStats.total_reservations, 1)) * 100 : 0}
                      sx={{ mt: 1 }}
                      color="success"
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
          </>
        )}

        {/* Recent Activity */}
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                  <RecentIcon color="primary" />
                  Đơn Hàng Gần Đây
                </Typography>
                {dashboardStats?.recent_orders && dashboardStats.recent_orders.length > 0 ? (
                  <List dense>
                    {dashboardStats.recent_orders.map((order) => (
                      <ListItem key={order.id} divider>
                        <ListItemAvatar>
                          <Avatar sx={{ bgcolor: getStatusColor(order.status) }}>
                            <OrdersIcon />
                          </Avatar>
                        </ListItemAvatar>
                        <ListItemText
                          primary={
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <Typography variant="subtitle2">
                                {order.order_number}
                              </Typography>
                              <Chip 
                                label={getStatusText(order.status)}
                                size="small"
                                sx={{ bgcolor: getStatusColor(order.status), color: 'white' }}
                              />
                            </Box>
                          }
                          secondary={
                            <Box>
                              <Typography variant="body2" color="textSecondary">
                                {order.customer_name} - Bàn {order.table_number}
                              </Typography>
                              <Typography variant="body2" sx={{ fontWeight: 'bold', color: 'success.main' }}>
                                {order.total_amount.toLocaleString()}đ
                              </Typography>
                            </Box>
                          }
                        />
                      </ListItem>
                    ))}
                  </List>
                ) : (
                  <Typography color="textSecondary" variant="body2">
                    Không có đơn hàng gần đây
                  </Typography>
                )}
                <Button
                  fullWidth
                  variant="outlined"
                  sx={{ mt: 2 }}
                  onClick={() => navigate('/admin/orders')}
                >
                  Xem tất cả đơn hàng
                </Button>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                  <PopularIcon color="warning" />
                  Món Ăn Phổ Biến
                </Typography>
                {dashboardStats?.popular_items && dashboardStats.popular_items.length > 0 ? (
                  <List dense>
                    {dashboardStats.popular_items.map((item, index) => (
                      <ListItem key={item.id} divider>
                        <ListItemAvatar>
                          <Avatar sx={{ bgcolor: '#ff9800', color: 'white' }}>
                            {index + 1}
                          </Avatar>
                        </ListItemAvatar>
                        <ListItemText
                          primary={
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <Typography variant="subtitle2">
                                {item.name}
                              </Typography>
                              <Chip 
                                label={`${item.total_ordered} lần`}
                                size="small"
                                color="warning"
                              />
                            </Box>
                          }
                          secondary={
                            <Typography variant="body2" sx={{ fontWeight: 'bold', color: 'success.main' }}>
                              {item.price.toLocaleString()}đ
                            </Typography>
                          }
                        />
                      </ListItem>
                    ))}
                  </List>
                ) : (
                  <Typography color="textSecondary" variant="body2">
                    Không có dữ liệu món ăn phổ biến
                  </Typography>
                )}
                <Button
                  fullWidth
                  variant="outlined"
                  sx={{ mt: 2 }}
                  onClick={() => navigate('/admin/menu')}
                >
                  Xem menu
                </Button>
              </CardContent>
            </Card>
          </Grid>

          {dashboardStats?.recent_reservations && dashboardStats.recent_reservations.length > 0 && (
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                    <ReservationIcon color="secondary" />
                    Đặt Bàn Gần Đây
                  </Typography>
                  <TableContainer>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Khách hàng</TableCell>
                          <TableCell>Bàn</TableCell>
                          <TableCell>Ngày đặt</TableCell>
                          <TableCell>Số người</TableCell>
                          <TableCell>Trạng thái</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {dashboardStats.recent_reservations.map((reservation) => (
                          <TableRow key={reservation.id}>
                            <TableCell>{reservation.customer_name}</TableCell>
                            <TableCell>Bàn {reservation.table_number}</TableCell>
                            <TableCell>
                              {new Date(reservation.reservation_date).toLocaleDateString('vi-VN')}
                            </TableCell>
                            <TableCell>{reservation.party_size} người</TableCell>
                            <TableCell>
                              <Chip 
                                label={getStatusText(reservation.status)}
                                size="small"
                                sx={{ bgcolor: getStatusColor(reservation.status), color: 'white' }}
                              />
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                  <Button
                    fullWidth
                    variant="outlined"
                    sx={{ mt: 2 }}
                    onClick={() => navigate('/admin/reservations')}
                  >
                    Xem tất cả đặt bàn
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          )}
        </Grid>
      </Box>
    </AdminLayout>
  );
};

export default Dashboard;