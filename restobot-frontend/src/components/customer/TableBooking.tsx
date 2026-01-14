import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  Stepper,
  Step,
  StepLabel,
  Divider,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Avatar
} from '@mui/material';
import {
  RestaurantOutlined as TableIcon,
  DateRange as DateIcon,
  People as PeopleIcon,
  LocationOn as LocationIcon,
  CheckCircle as ConfirmIcon,
  CheckCircle,
  ArrowBack as BackIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import { tableService } from '../../services/tableService';
import { Table, CreateReservationRequest } from '../../types';
import { useAuth } from '../../hooks/useAuth';
import { format, addDays } from 'date-fns';
import { vi } from 'date-fns/locale';

interface TableBookingProps {
  open: boolean;
  onClose: () => void;
  initialData?: {
    guests?: number;
    date?: string;
    time?: string;
  };
}

const TableBooking: React.FC<TableBookingProps> = ({ open, onClose, initialData }) => {
  const { user } = useAuth();
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Booking form data
  const [bookingData, setBookingData] = useState<{
    date: string;
    time: string;
    guests: number;
    selectedTable: Table | null;
    specialRequests: string;
    customerName: string;
    customerEmail: string;
    customerPhone: string;
  }>({
    date: initialData?.date || format(new Date(), 'yyyy-MM-dd'),
    time: initialData?.time || '19:00',
    guests: initialData?.guests || 2,
    selectedTable: null,
    specialRequests: '',
    customerName: user?.full_name || '',
    customerEmail: user?.email || '',
    customerPhone: user?.phone || ''
  });

  // Available tables
  const [availableTables, setAvailableTables] = useState<Table[]>([]);
  const [suggestedTimes, setSuggestedTimes] = useState<string[]>([]);

  const steps = ['Chọn thời gian', 'Chọn bàn', 'Thông tin khách hàng', 'Xác nhận'];

  // Business hours with lunch break validation
  const getAvailableTimeSlots = () => {
    const selectedDate = new Date(bookingData.date);
    const today = new Date();
    const isWeekday = selectedDate.getDay() >= 1 && selectedDate.getDay() <= 5; // Mon-Fri
    
    let timeSlots = [
      // Morning slots
      '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '13:30',
      // Evening slots  
      '17:00', '17:30', '18:00', '18:30', '19:00', '19:30',
      '20:00', '20:30', '21:00', '21:30'
    ];

    // Remove lunch break hours (14:00-17:00) for weekdays
    if (isWeekday) {
      timeSlots = timeSlots.filter(time => {
        const [hour] = time.split(':').map(Number);
        return !(hour >= 14 && hour < 17); // Remove 14:00-16:30
      });
    }

    // If today, remove past time slots
    if (selectedDate.toDateString() === today.toDateString()) {
      const currentHour = today.getHours();
      const currentMinute = today.getMinutes();
      
      timeSlots = timeSlots.filter(time => {
        const [hour, minute] = time.split(':').map(Number);
        return hour > currentHour || (hour === currentHour && minute > currentMinute + 60); // 1 hour advance booking
      });
    }

    return timeSlots;
  };

  const timeSlots = getAvailableTimeSlots();

  useEffect(() => {
    if (open && initialData) {
      setBookingData(prev => ({
        ...prev,
        date: initialData.date || prev.date,
        time: initialData.time || prev.time,
        guests: initialData.guests || prev.guests
      }));
    }
  }, [open, initialData]);

  // Check availability when date, time, or guests change
  const checkAvailability = useCallback(async () => {
    if (!bookingData.date || !bookingData.time || bookingData.guests <= 0) return;

    try {
      setLoading(true);
      const result = await tableService.checkAvailability({
        date: bookingData.date,
        time: bookingData.time,
        guests: bookingData.guests
      });

      setAvailableTables(result.available_tables);
      setSuggestedTimes(result.suggested_times || []);

      if (!result.available && result.suggested_times?.length) {
        setError(`Không có bàn trống lúc ${bookingData.time}. Thời gian khác có thể đặt: ${result.suggested_times.join(', ')}`);
      } else if (!result.available) {
        setError('Không có bàn trống cho thời gian này. Vui lòng chọn thời gian khác.');
      } else {
        setError(null);
      }
    } catch (err) {
      console.error('Error checking availability:', err);
      setError('Lỗi khi kiểm tra bàn trống. Vui lòng thử lại.');
    } finally {
      setLoading(false);
    }
  }, [bookingData.date, bookingData.time, bookingData.guests]);

  useEffect(() => {
    if (bookingData.date && bookingData.time && bookingData.guests > 0) {
      checkAvailability();
    }
  }, [bookingData.date, bookingData.time, bookingData.guests, checkAvailability]);

  const handleNext = () => {
    if (activeStep === 0 && (!bookingData.date || !bookingData.time || availableTables.length === 0)) {
      setError('Vui lòng chọn thời gian và đảm bảo có bàn trống.');
      return;
    }
    if (activeStep === 1 && !bookingData.selectedTable) {
      setError('Vui lòng chọn bàn.');
      return;
    }
    if (activeStep === 2 && (!bookingData.customerName || !bookingData.customerEmail)) {
      setError('Vui lòng nhập đầy đủ thông tin khách hàng.');
      return;
    }

    setError(null);
    setActiveStep(prev => prev + 1);
  };

  const handleBack = () => {
    setActiveStep(prev => prev - 1);
  };

  const handleSubmit = async () => {
    if (!bookingData.selectedTable || !user) {
      setError('Thông tin đặt bàn không đầy đủ.');
      return;
    }

    try {
      setLoading(true);
      const reservationData: CreateReservationRequest = {
        table_id: bookingData.selectedTable.id,
        reservation_date: `${bookingData.date}T${bookingData.time}:00`,
        party_size: bookingData.guests,
        special_requests: bookingData.specialRequests || undefined,
        customer_name: bookingData.customerName,
        customer_email: bookingData.customerEmail,
        customer_phone: bookingData.customerPhone || undefined
      };

      const result = await tableService.bookTable(reservationData);
      setSuccess(`Đặt bàn thành công! Mã đặt bàn: ${result.id}`);
      
      // Reset form after success
      setTimeout(() => {
        setActiveStep(0);
        setBookingData(prev => ({
          ...prev,
          selectedTable: null,
          specialRequests: ''
        }));
        onClose();
      }, 2000);

    } catch (err: any) {
      console.error('Error booking table:', err);
      setError(err.message || 'Lỗi khi đặt bàn. Vui lòng thử lại.');
    } finally {
      setLoading(false);
    }
  };

  const getTableStatusColor = (status: string) => {
    switch (status) {
      case 'available': return 'success';
      case 'occupied': return 'warning';
      case 'reserved': return 'error';
      default: return 'default';
    }
  };

  const getTableStatusLabel = (status: string) => {
    switch (status) {
      case 'available': return 'Trống';
      case 'occupied': return 'Đang sử dụng';
      case 'reserved': return 'Đã đặt';
      default: return status;
    }
  };

  const getMinDate = () => {
    return format(new Date(), 'yyyy-MM-dd');
  };

  const getMaxDate = () => {
    return format(addDays(new Date(), 30), 'yyyy-MM-dd');
  };

  const isTimeSlotAvailable = (time: string) => {
    // Check business hours validation
    const [hour] = time.split(':').map(Number);
    const selectedDate = new Date(bookingData.date);
    const isWeekday = selectedDate.getDay() >= 1 && selectedDate.getDay() <= 5; // Mon-Fri
    
    // Check lunch break (14:00-17:00 on weekdays)
    if (isWeekday && hour >= 14 && hour < 17) {
      return false;
    }
    
    // Check operating hours (10:00-22:00)
    if (hour < 10 || hour >= 22) {
      return false;
    }
    
    // Check suggested times if available
    if (suggestedTimes.length > 0) {
      return suggestedTimes.includes(time);
    }
    
    return true;
  };

  const renderStepContent = () => {
    switch (activeStep) {
      case 0: // Date & Time Selection
        return (
          <Box>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <DateIcon color="primary" />
              Chọn ngày và thời gian
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Ngày đặt bàn"
                  type="date"
                  value={bookingData.date}
                  onChange={(e) => setBookingData(prev => ({ ...prev, date: e.target.value }))}
                  inputProps={{
                    min: getMinDate(),
                    max: getMaxDate()
                  }}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Số khách</InputLabel>
                  <Select
                    value={bookingData.guests}
                    onChange={(e) => setBookingData(prev => ({ ...prev, guests: Number(e.target.value) }))}
                    label="Số khách"
                  >
                    {Array.from({ length: 10 }, (_, i) => i + 1).map(num => (
                      <MenuItem key={num} value={num}>{num} người</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12}>
                <Typography variant="subtitle1" gutterBottom>
                  Chọn giờ đặt bàn
                </Typography>
                <Grid container spacing={1}>
                  {timeSlots.map(time => (
                    <Grid item xs={6} sm={4} md={3} key={time}>
                      <Button
                        fullWidth
                        variant={bookingData.time === time ? 'contained' : 'outlined'}
                        disabled={!isTimeSlotAvailable(time)}
                        onClick={() => setBookingData(prev => ({ ...prev, time }))}
                        sx={{ 
                          py: 1.5,
                          opacity: !isTimeSlotAvailable(time) ? 0.5 : 1
                        }}
                      >
                        {time}
                      </Button>
                    </Grid>
                  ))}
                </Grid>
              </Grid>

              {availableTables.length > 0 && (
                <Grid item xs={12}>
                  <Alert severity="success" icon={<CheckCircle />}>
                    Tìm thấy {availableTables.length} bàn trống cho {bookingData.guests} người vào {bookingData.time} ngày {format(new Date(bookingData.date), 'dd/MM/yyyy', { locale: vi })}
                  </Alert>
                </Grid>
              )}

              {suggestedTimes.length > 0 && availableTables.length === 0 && (
                <Grid item xs={12}>
                  <Alert severity="warning" icon={<InfoIcon />}>
                    Thời gian khác có thể đặt: {suggestedTimes.join(', ')}
                  </Alert>
                </Grid>
              )}
            </Grid>
          </Box>
        );

      case 1: // Table Selection
        return (
          <Box>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <TableIcon color="primary" />
              Chọn bàn ({availableTables.length} bàn có sẵn)
            </Typography>

            <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
              Ngày: {format(new Date(bookingData.date), 'dd/MM/yyyy', { locale: vi })} | 
              Thời gian: {bookingData.time} | 
              Số khách: {bookingData.guests} người
            </Typography>

            <Grid container spacing={2}>
              {availableTables.map(table => (
                <Grid item xs={12} sm={6} md={4} key={table.id}>
                  <Card 
                    sx={{ 
                      cursor: 'pointer',
                      border: bookingData.selectedTable?.id === table.id ? 2 : 1,
                      borderColor: bookingData.selectedTable?.id === table.id ? 'primary.main' : 'divider',
                      '&:hover': {
                        boxShadow: 2,
                        borderColor: 'primary.light'
                      }
                    }}
                    onClick={() => setBookingData(prev => ({ ...prev, selectedTable: table }))}
                  >
                    <CardContent sx={{ textAlign: 'center', py: 2 }}>
                      <Avatar 
                        sx={{ 
                          bgcolor: 'primary.main', 
                          mx: 'auto', 
                          mb: 1,
                          width: 48,
                          height: 48
                        }}
                      >
                        <TableIcon />
                      </Avatar>
                      
                      <Typography variant="h6" gutterBottom>
                        Bàn {table.table_number}
                      </Typography>
                      
                      <Chip
                        label={`${table.capacity} người`}
                        size="small"
                        color="primary"
                        sx={{ mb: 1 }}
                      />
                      
                      {table.location && (
                        <Typography variant="body2" color="textSecondary" sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
                          <LocationIcon fontSize="small" />
                          {table.location}
                        </Typography>
                      )}

                      <Chip
                        label={getTableStatusLabel(table.current_status)}
                        size="small"
                        color={getTableStatusColor(table.current_status) as any}
                        sx={{ mt: 1 }}
                      />

                      {bookingData.selectedTable?.id === table.id && (
                        <Box sx={{ mt: 1 }}>
                          <CheckCircle color="primary" />
                        </Box>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        );

      case 2: // Customer Information
        return (
          <Box>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <PeopleIcon color="primary" />
              Thông tin khách hàng
            </Typography>

            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Họ và tên *"
                  value={bookingData.customerName}
                  onChange={(e) => setBookingData(prev => ({ ...prev, customerName: e.target.value }))}
                  required
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Email *"
                  type="email"
                  value={bookingData.customerEmail}
                  onChange={(e) => setBookingData(prev => ({ ...prev, customerEmail: e.target.value }))}
                  required
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Số điện thoại"
                  value={bookingData.customerPhone}
                  onChange={(e) => setBookingData(prev => ({ ...prev, customerPhone: e.target.value }))}
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Yêu cầu đặc biệt"
                  multiline
                  rows={3}
                  value={bookingData.specialRequests}
                  onChange={(e) => setBookingData(prev => ({ ...prev, specialRequests: e.target.value }))}
                  placeholder="Ví dụ: Bàn gần cửa sổ, ghế trẻ em, tiệc sinh nhật..."
                />
              </Grid>
            </Grid>
          </Box>
        );

      case 3: // Confirmation
        return (
          <Box>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <ConfirmIcon color="primary" />
              Xác nhận đặt bàn
            </Typography>

            <Paper elevation={1} sx={{ p: 3, bgcolor: 'grey.50' }}>
              <List>
                <ListItem>
                  <ListItemIcon><DateIcon /></ListItemIcon>
                  <ListItemText 
                    primary="Ngày giờ đặt bàn"
                    secondary={`${format(new Date(bookingData.date), 'dd/MM/yyyy', { locale: vi })} lúc ${bookingData.time}`}
                  />
                </ListItem>
                
                <ListItem>
                  <ListItemIcon><TableIcon /></ListItemIcon>
                  <ListItemText 
                    primary="Bàn đã chọn"
                    secondary={`Bàn ${bookingData.selectedTable?.table_number} (${bookingData.selectedTable?.capacity} người)`}
                  />
                </ListItem>

                <ListItem>
                  <ListItemIcon><PeopleIcon /></ListItemIcon>
                  <ListItemText 
                    primary="Số khách"
                    secondary={`${bookingData.guests} người`}
                  />
                </ListItem>

                <ListItem>
                  <ListItemIcon><PeopleIcon /></ListItemIcon>
                  <ListItemText 
                    primary="Khách hàng"
                    secondary={`${bookingData.customerName} - ${bookingData.customerEmail}`}
                  />
                </ListItem>

                {bookingData.specialRequests && (
                  <ListItem>
                    <ListItemIcon><InfoIcon /></ListItemIcon>
                    <ListItemText 
                      primary="Yêu cầu đặc biệt"
                      secondary={bookingData.specialRequests}
                    />
                  </ListItem>
                )}
              </List>
            </Paper>

            <Alert severity="info" sx={{ mt: 2 }}>
              Sau khi đặt bàn, nhà hàng sẽ liên hệ với bạn trong vòng 15 phút để xác nhận.
            </Alert>
          </Box>
        );

      default:
        return null;
    }
  };

  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth="md" 
      fullWidth
      PaperProps={{ sx: { minHeight: '70vh' } }}
    >
      <DialogTitle sx={{ bgcolor: 'primary.main', color: 'white', pb: 2 }}>
        <Typography variant="h5" component="div">
          Đặt bàn nhà hàng
        </Typography>
        <Stepper activeStep={activeStep} sx={{ mt: 2 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel 
                sx={{
                  '& .MuiStepLabel-label': { color: 'white !important' },
                  '& .MuiStepIcon-root': { color: 'rgba(255,255,255,0.7)' },
                  '& .MuiStepIcon-root.Mui-active': { color: 'white' },
                  '& .MuiStepIcon-root.Mui-completed': { color: 'white' }
                }}
              >
                {label}
              </StepLabel>
            </Step>
          ))}
        </Stepper>
      </DialogTitle>

      <DialogContent sx={{ p: 3 }}>
        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
            <CircularProgress />
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

        {!loading && renderStepContent()}
      </DialogContent>

      <Divider />

      <DialogActions sx={{ p: 2 }}>
        <Button onClick={onClose} disabled={loading}>
          Hủy
        </Button>
        
        {activeStep > 0 && (
          <Button 
            startIcon={<BackIcon />}
            onClick={handleBack}
            disabled={loading}
          >
            Quay lại
          </Button>
        )}
        
        {activeStep < steps.length - 1 ? (
          <Button 
            variant="contained" 
            onClick={handleNext}
            disabled={loading}
          >
            Tiếp theo
          </Button>
        ) : (
          <Button 
            variant="contained" 
            onClick={handleSubmit}
            disabled={loading || !bookingData.selectedTable}
            color="primary"
          >
            Xác nhận đặt bàn
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default TableBooking;