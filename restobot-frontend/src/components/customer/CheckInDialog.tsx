import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Alert,
  CircularProgress,
  Chip,
  Divider
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Schedule as ScheduleIcon,
  EventSeat as TableIcon,
  People as PeopleIcon
} from '@mui/icons-material';

interface Reservation {
  id: number;
  table_number?: string;
  reservation_time: string;
  number_of_guests: number;
  status: string;
}

interface CheckInDialogProps {
  open: boolean;
  onClose: () => void;
  reservation: Reservation | null;
  onCheckInSuccess?: () => void;
}

const CheckInDialog: React.FC<CheckInDialogProps> = ({
  open,
  onClose,
  reservation,
  onCheckInSuccess
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [arrivalInfo, setArrivalInfo] = useState<any>(null);

  const handleCheckIn = async () => {
    if (!reservation) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/arrivals/record', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          reservation_id: reservation.id
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to check in');
      }

      const data = await response.json();
      setArrivalInfo(data);
      setSuccess(true);

      // Call success callback after a short delay
      setTimeout(() => {
        if (onCheckInSuccess) {
          onCheckInSuccess();
        }
        handleClose();
      }, 2000);

    } catch (err: any) {
      console.error('Check-in error:', err);
      setError(err.message || 'Không thể check-in. Vui lòng thử lại.');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setSuccess(false);
    setArrivalInfo(null);
    setError(null);
    onClose();
  };

  const getArrivalStatusLabel = (status: string) => {
    const labels: Record<string, { text: string; color: any }> = {
      early: { text: 'Đến sớm', color: 'info' },
      on_time: { text: 'Đúng giờ', color: 'success' },
      late: { text: 'Đến muộn', color: 'warning' },
      very_late: { text: 'Đến rất muộn', color: 'error' }
    };
    return labels[status] || { text: status, color: 'default' };
  };

  const formatTime = (isoString: string) => {
    const date = new Date(isoString);
    return date.toLocaleTimeString('vi-VN', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (!reservation) return null;

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <TableIcon sx={{ mr: 1, color: 'primary.main' }} />
          <Typography variant="h6">
            Check-in tại nhà hàng
          </Typography>
        </Box>
      </DialogTitle>

      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {success && arrivalInfo ? (
          <Box>
            <Alert severity="success" icon={<CheckCircleIcon />} sx={{ mb: 2 }}>
              Đã check-in thành công!
            </Alert>

            <Box sx={{ p: 2, bgcolor: 'background.paper', borderRadius: 1 }}>
              <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                Thông tin check-in
              </Typography>

              <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <ScheduleIcon sx={{ mr: 1, fontSize: 20, color: 'text.secondary' }} />
                    <Typography variant="body2">
                      Giờ đặt bàn
                    </Typography>
                  </Box>
                  <Typography variant="body2" fontWeight="medium">
                    {formatTime(arrivalInfo.reservation_time)}
                  </Typography>
                </Box>

                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <CheckCircleIcon sx={{ mr: 1, fontSize: 20, color: 'success.main' }} />
                    <Typography variant="body2">
                      Giờ đến
                    </Typography>
                  </Box>
                  <Typography variant="body2" fontWeight="medium">
                    {formatTime(arrivalInfo.arrival_time)}
                  </Typography>
                </Box>

                <Divider />

                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Typography variant="body2">
                    Trạng thái
                  </Typography>
                  <Chip
                    label={getArrivalStatusLabel(arrivalInfo.arrival_status).text}
                    color={getArrivalStatusLabel(arrivalInfo.arrival_status).color}
                    size="small"
                  />
                </Box>

                {arrivalInfo.minutes_difference !== 0 && (
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Typography variant="body2" color="textSecondary">
                      Chênh lệch
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      {arrivalInfo.minutes_difference > 0 ? '+' : ''}
                      {arrivalInfo.minutes_difference} phút
                    </Typography>
                  </Box>
                )}
              </Box>
            </Box>

            <Typography variant="body2" color="textSecondary" sx={{ mt: 2, textAlign: 'center' }}>
              Bàn của bạn đang được chuẩn bị. Nhân viên sẽ dẫn bạn vào ngay!
            </Typography>
          </Box>
        ) : (
          <Box>
            <Typography variant="body1" paragraph>
              Xác nhận bạn đã đến nhà hàng?
            </Typography>

            <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <TableIcon sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="body2">
                  <strong>Bàn:</strong> {reservation.table_number || 'Chưa xác định'}
                </Typography>
              </Box>

              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <ScheduleIcon sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="body2">
                  <strong>Giờ đặt:</strong> {formatTime(reservation.reservation_time)}
                </Typography>
              </Box>

              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <PeopleIcon sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="body2">
                  <strong>Số người:</strong> {reservation.number_of_guests}
                </Typography>
              </Box>
            </Box>

            <Alert severity="info" sx={{ mt: 2 }}>
              Nhấn "Check-in" để thông báo bạn đã đến. Nhân viên sẽ dẫn bạn vào bàn ngay.
            </Alert>
          </Box>
        )}
      </DialogContent>

      <DialogActions>
        {!success && (
          <>
            <Button onClick={handleClose} disabled={loading}>
              Hủy
            </Button>
            <Button
              onClick={handleCheckIn}
              variant="contained"
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} /> : <CheckCircleIcon />}
            >
              {loading ? 'Đang check-in...' : 'Check-in'}
            </Button>
          </>
        )}
        {success && (
          <Button onClick={handleClose} variant="contained" color="success">
            Đóng
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default CheckInDialog;