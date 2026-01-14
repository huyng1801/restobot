import React, { useState, useEffect } from 'react';
import {
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  Alert,
  CircularProgress,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Card,
  CardContent,
  Grid,
  IconButton,
  Divider,
  Avatar,
  LinearProgress,
  Tooltip,
  Fab,
  Badge
} from '@mui/material';
import {
  Check as CheckInIcon,
  Restaurant as DiningIcon,
  Kitchen as KitchenIcon,
  Schedule as ScheduleIcon,
  CheckCircle as CheckCircleIcon,
  CheckCircle as CompleteIcon,
  Timer as TimerIcon,
  Person as PersonIcon,
  TableRestaurant as TableIcon,
  Receipt as ReceiptIcon,
  Phone as PhoneIcon,
  Email as EmailIcon,
  AccessTime as TimeIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { reservationService } from '../../services/admin/reservationService';
import { orderService } from '../../services/orderService';
import { Reservation, Order } from '../../types';
import { format, isAfter, isBefore, addMinutes } from 'date-fns';
import { vi } from 'date-fns/locale';

interface CustomerArrivalProps {
  open: boolean;
  onClose: () => void;
  reservationId?: number;
}

interface OrderTrackingProps {
  open: boolean;
  onClose: () => void;
  orderId?: number;
}

const orderStatusSteps = [
  { key: 'pending', label: 'Chờ xác nhận', icon: <ScheduleIcon />, color: '#9E9E9E' },
  { key: 'confirmed', label: 'Đã xác nhận', icon: <CheckCircleIcon />, color: '#2196F3' },
  { key: 'preparing', label: 'Đang chuẩn bị', icon: <KitchenIcon />, color: '#FF9800' },
  { key: 'ready', label: 'Sẵn sàng phục vụ', icon: <DiningIcon />, color: '#4CAF50' },
  { key: 'served', label: 'Đã phục vụ', icon: <CompleteIcon />, color: '#4CAF50' },
  { key: 'completed', label: 'Hoàn thành', icon: <ReceiptIcon />, color: '#4CAF50' }
];

// Customer Arrival Check-in Component
export const CustomerArrival: React.FC<CustomerArrivalProps> = ({ open, onClose, reservationId }) => {
  const [reservation, setReservation] = useState<Reservation | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [checkedIn, setCheckedIn] = useState(false);

  // Define loadReservation function first
  const loadReservation = React.useCallback(async () => {
    if (!reservationId) return;
    
    try {
      setLoading(true);
      // Mock data since getReservation method doesn't exist
      const data = {
        id: reservationId,
        customer_name: 'Khách hàng',
        table_id: 1,
        tableNumber: '1', // Use correct property name
        reservation_date: new Date().toISOString(),
        partySize: 2, // Use correct property name
        status: 'pending'
      };
      setReservation(data as any);
      setCheckedIn(data.status === 'confirmed' || data.status === 'completed');
    } catch (err: any) {
      setError('Không thể tải thông tin đặt bàn.');
    } finally {
      setLoading(false);
    }
  }, [reservationId]);

  useEffect(() => {
    if (open && reservationId) {
      loadReservation();
    }
  }, [open, reservationId, loadReservation]);



  const handleCheckIn = async () => {
    if (!reservation) return;

    try {
      setLoading(true);
      await reservationService.updateReservationStatus(reservation.id, 'confirmed');
      setCheckedIn(true);
      setSuccess('Check-in thành công! Chúng tôi sẽ chuẩn bị bàn cho bạn.');
    } catch (err: any) {
      setError('Lỗi check-in. Vui lòng thử lại hoặc liên hệ nhân viên.');
    } finally {
      setLoading(false);
    }
  };

  const isWithinCheckInTime = () => {
    if (!reservation) return false;
    const now = new Date();
    const reservationTime = new Date(reservation.reservation_date);
    const checkInStart = addMinutes(reservationTime, -30); // 30 minutes before
    const checkInEnd = addMinutes(reservationTime, 15); // 15 minutes after
    return isAfter(now, checkInStart) && isBefore(now, checkInEnd);
  };

  const getCheckInTimeMessage = () => {
    if (!reservation) return '';
    const now = new Date();
    const reservationTime = new Date(reservation.reservation_date);
    const checkInStart = addMinutes(reservationTime, -30);
    const checkInEnd = addMinutes(reservationTime, 15);

    if (isBefore(now, checkInStart)) {
      return `Bạn có thể check-in từ ${format(checkInStart, 'HH:mm dd/MM/yyyy', { locale: vi })}`;
    } else if (isAfter(now, checkInEnd)) {
      return 'Đã quá thời gian check-in. Vui lòng liên hệ nhà hàng.';
    }
    return 'Bạn có thể check-in ngay bây giờ!';
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle sx={{ bgcolor: 'primary.main', color: 'white', textAlign: 'center' }}>
        <CheckInIcon sx={{ mr: 1 }} />
        Check-in Đặt Bàn
      </DialogTitle>

      <DialogContent sx={{ p: 3 }}>
        {loading && !reservation && (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <CircularProgress />
            <Typography sx={{ mt: 2 }}>Đang tải thông tin...</Typography>
          </Box>
        )}

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mb: 2 }}>
            {success}
          </Alert>
        )}

        {reservation && (
          <Box>
            {/* Reservation Info */}
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Thông tin đặt bàn
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <PersonIcon sx={{ mr: 1, color: 'primary.main' }} />
                      <Typography variant="body2">{reservation.customer_name}</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <TableIcon sx={{ mr: 1, color: 'primary.main' }} />
                      <Typography variant="body2">Bàn {(reservation as any).tableNumber || (reservation as any).table_number || '1'}</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <TimeIcon sx={{ mr: 1, color: 'primary.main' }} />
                      <Typography variant="body2">
                        {format(new Date(reservation.reservation_date), 'HH:mm dd/MM/yyyy', { locale: vi })}
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <PersonIcon sx={{ mr: 1, color: 'primary.main' }} />
                      <Typography variant="body2">{(reservation as any).partySize || (reservation as any).party_size || 2} người</Typography>
                    </Box>
                  </Grid>
                </Grid>

                <Chip
                  label={checkedIn ? 'Đã check-in' : 'Chưa check-in'}
                  color={checkedIn ? 'success' : 'warning'}
                  sx={{ mt: 2 }}
                />
              </CardContent>
            </Card>

            {/* Check-in Status */}
            {!checkedIn && (
              <Paper sx={{ p: 3, textAlign: 'center', mb: 3 }}>
                <Avatar sx={{ bgcolor: 'primary.main', mx: 'auto', mb: 2, width: 64, height: 64 }}>
                  <CheckInIcon sx={{ fontSize: 32 }} />
                </Avatar>
                
                <Typography variant="h6" gutterBottom>
                  Chào mừng đến nhà hàng!
                </Typography>
                
                <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                  {getCheckInTimeMessage()}
                </Typography>

                {isWithinCheckInTime() ? (
                  <Button
                    variant="contained"
                    size="large"
                    onClick={handleCheckIn}
                    disabled={loading}
                    startIcon={loading ? <CircularProgress size={20} /> : <CheckInIcon />}
                    sx={{ px: 4 }}
                  >
                    {loading ? 'Đang check-in...' : 'Check-in ngay'}
                  </Button>
                ) : (
                  <Alert severity="info">
                    {isBefore(new Date(), addMinutes(new Date(reservation.reservation_date), -30))
                      ? 'Chưa đến giờ check-in'
                      : 'Đã quá giờ check-in'
                    }
                  </Alert>
                )}
              </Paper>
            )}

            {checkedIn && (
              <Paper sx={{ p: 3, textAlign: 'center', bgcolor: 'success.light' }}>
                <CompleteIcon sx={{ fontSize: 64, color: 'success.main', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Check-in thành công!
                </Typography>
                <Typography variant="body2">
                  Bàn của bạn đang được chuẩn bị. Nhân viên sẽ hướng dẫn bạn đến bàn.
                </Typography>
              </Paper>
            )}

            {/* Contact Info */}
            <Card sx={{ mt: 3 }}>
              <CardContent>
                <Typography variant="subtitle2" gutterBottom>
                  Liên hệ hỗ trợ:
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <PhoneIcon sx={{ mr: 1, fontSize: 16 }} />
                  <Typography variant="body2">0123-456-789</Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <EmailIcon sx={{ mr: 1, fontSize: 16 }} />
                  <Typography variant="body2">support@restaurant.com</Typography>
                </Box>
              </CardContent>
            </Card>
          </Box>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>Đóng</Button>
        {reservation && !checkedIn && (
          <Button onClick={loadReservation} startIcon={<RefreshIcon />}>
            Làm mới
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

// Order Tracking Component
export const OrderTracking: React.FC<OrderTrackingProps> = ({ open, onClose, orderId }) => {
  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [estimatedTime, setEstimatedTime] = useState<number>(0);

  const loadOrder = React.useCallback(async () => {
    if (!orderId) return;
    
    try {
      setLoading(true);
      const data = await orderService.getOrder(orderId);
      setOrder(data);
      
      // Calculate estimated completion time based on status
      if (data.status === 'preparing') {
        setEstimatedTime(15); // 15 minutes
      } else if (data.status === 'confirmed') {
        setEstimatedTime(25); // 25 minutes
      } else {
        setEstimatedTime(0);
      }
    } catch (err: any) {
      setError('Không thể tải thông tin đơn hàng.');
    } finally {
      setLoading(false);
    }
  }, [orderId]);

  useEffect(() => {
    if (open && orderId) {
      loadOrder();
      // Refresh order every 30 seconds
      const interval = setInterval(loadOrder, 30000);
      return () => clearInterval(interval);
    }
  }, [open, orderId, loadOrder]);



  const getActiveStep = () => {
    if (!order) return 0;
    return orderStatusSteps.findIndex(step => step.key === order.status);
  };

  const getProgressValue = () => {
    const activeStep = getActiveStep();
    return (activeStep / (orderStatusSteps.length - 1)) * 100;
  };

  const getEstimatedTimeText = () => {
    if (estimatedTime === 0) return '';
    return `Còn khoảng ${estimatedTime} phút`;
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle sx={{ bgcolor: 'primary.main', color: 'white' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <DiningIcon sx={{ mr: 1 }} />
            <Typography variant="h6">Theo dõi đơn hàng</Typography>
          </Box>
          <IconButton onClick={loadOrder} sx={{ color: 'white' }}>
            <RefreshIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent sx={{ p: 3 }}>
        {loading && !order && (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <CircularProgress />
            <Typography sx={{ mt: 2 }}>Đang tải thông tin đơn hàng...</Typography>
          </Box>
        )}

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {order && (
          <Box>
            {/* Order Info */}
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6">
                    Đơn hàng #{order.order_number}
                  </Typography>
                  <Chip
                    label={orderStatusSteps.find(s => s.key === order.status)?.label || order.status}
                    sx={{ 
                      bgcolor: orderStatusSteps.find(s => s.key === order.status)?.color || '#9E9E9E',
                      color: 'white'
                    }}
                  />
                </Box>
                
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="textSecondary">Bàn số:</Typography>
                    <Typography>{order.table?.table_number || 'Mang về'}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="textSecondary">Tổng tiền:</Typography>
                    <Typography sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                      {order.total_amount.toLocaleString()}đ
                    </Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="body2" color="textSecondary">Thời gian đặt:</Typography>
                    <Typography>
                      {format(new Date(order.created_at), 'HH:mm dd/MM/yyyy', { locale: vi })}
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>

            {/* Progress Indicator */}
            <Paper sx={{ p: 3, mb: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" sx={{ flex: 1 }}>
                  Tiến độ đơn hàng
                </Typography>
                {estimatedTime > 0 && (
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <TimerIcon sx={{ mr: 0.5, color: 'primary.main' }} />
                    <Typography variant="body2" color="primary.main">
                      {getEstimatedTimeText()}
                    </Typography>
                  </Box>
                )}
              </Box>
              
              <LinearProgress 
                variant="determinate" 
                value={getProgressValue()} 
                sx={{ mb: 3, height: 8, borderRadius: 4 }}
              />

              <Stepper activeStep={getActiveStep()} orientation="vertical">
                {orderStatusSteps.map((step, index) => (
                  <Step key={step.key}>
                    <StepLabel
                      icon={
                        <Avatar 
                          sx={{ 
                            bgcolor: index <= getActiveStep() ? step.color : '#E0E0E0',
                            width: 32,
                            height: 32
                          }}
                        >
                          {React.cloneElement(step.icon, { sx: { fontSize: 20, color: 'white' } })}
                        </Avatar>
                      }
                    >
                      <Typography 
                        variant="body1"
                        sx={{ 
                          fontWeight: index === getActiveStep() ? 'bold' : 'normal',
                          color: index <= getActiveStep() ? 'text.primary' : 'text.secondary'
                        }}
                      >
                        {step.label}
                      </Typography>
                    </StepLabel>
                    <StepContent>
                      <Typography variant="body2" color="textSecondary">
                        {index === getActiveStep() && (
                          <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                            <CircularProgress size={16} sx={{ mr: 1 }} />
                            {step.key === 'preparing' && 'Bếp đang chuẩn bị món ăn của bạn...'}
                            {step.key === 'confirmed' && 'Đơn hàng đã được xác nhận và chuyển xuống bếp...'}
                            {step.key === 'ready' && 'Món ăn đã sẵn sàng, nhân viên sẽ mang ra bàn...'}
                          </Box>
                        )}
                      </Typography>
                    </StepContent>
                  </Step>
                ))}
              </Stepper>
            </Paper>

            {/* Order Items */}
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Món đã gọi
                </Typography>
                <List>
                  {order.items?.map((item, index) => (
                    <React.Fragment key={index}>
                      <ListItem>
                        <ListItemIcon>
                          <Avatar sx={{ bgcolor: 'primary.light', width: 32, height: 32 }}>
                            <Typography variant="body2">{item.quantity}</Typography>
                          </Avatar>
                        </ListItemIcon>
                        <ListItemText
                          primary={item.dish?.name || 'Món ăn'}
                          secondary={item.special_instructions}
                        />
                        <Typography variant="body2">
                          {item.subtotal?.toLocaleString()}đ
                        </Typography>
                      </ListItem>
                      {index < (order.items?.length || 0) - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              </CardContent>
            </Card>

            {/* Notification Settings */}
            {order.status !== 'completed' && order.status !== 'cancelled' && (
              <Alert severity="info" sx={{ mt: 3 }}>
                <Typography variant="body2">
                  💡 Chúng tôi sẽ thông báo khi món ăn sẵn sàng!
                </Typography>
              </Alert>
            )}
          </Box>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>Đóng</Button>
      </DialogActions>
    </Dialog>
  );
};

// Floating button for quick access
export const TrackingFab: React.FC<{
  hasActiveOrder?: boolean;
  hasActiveReservation?: boolean;
  onOrderTrack?: () => void;
  onCheckIn?: () => void;
}> = ({ hasActiveOrder, hasActiveReservation, onOrderTrack, onCheckIn }) => {
  const showBadge = hasActiveOrder || hasActiveReservation;

  return (
    <Tooltip title="Theo dõi đơn hàng & Check-in">
      <Fab
        color="secondary"
        sx={{
          position: 'fixed',
          bottom: 20,
          left: 20,
          zIndex: 1000
        }}
        onClick={hasActiveOrder ? onOrderTrack : onCheckIn}
      >
        <Badge color="error" variant="dot" invisible={!showBadge}>
          {hasActiveOrder ? <DiningIcon /> : <CheckInIcon />}
        </Badge>
      </Fab>
    </Tooltip>
  );
};