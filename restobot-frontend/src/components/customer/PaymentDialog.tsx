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
  Divider,
  List,
  ListItem,
  ListItemText,
  Alert,
  RadioGroup,
  FormControlLabel,
  Radio,
  FormControl,
  TextField,
  Card,
  CardContent,
  IconButton,
  CircularProgress,
  Stepper,
  Step,
  StepLabel,
  Grid
} from '@mui/material';
import {
  Payment as PaymentIcon,
  CreditCard as CardIcon,
  AccountBalance as BankIcon,
  QrCode2 as QrIcon,
  Money as CashIcon,
  CheckCircle as ConfirmIcon,
  ContentCopy as CopyIcon,
  Timer as TimerIcon
} from '@mui/icons-material';
import { orderService } from '../../services/orderService';
import { Order, OrderItem } from '../../types';

interface PaymentDialogProps {
  open: boolean;
  onClose: () => void;
  order: Order | null;
  onPaymentComplete?: (paymentId: string) => void;
}

interface PaymentMethod {
  id: string;
  name: string;
  icon: React.ReactNode;
  description: string;
  processingTime: string;
  enabled: boolean;
}

const paymentMethods: PaymentMethod[] = [
  {
    id: 'cash',
    name: 'Tiền mặt',
    icon: <CashIcon />,
    description: 'Thanh toán trực tiếp tại quầy',
    processingTime: 'Ngay lập tức',
    enabled: true
  },
  {
    id: 'card',
    name: 'Thẻ tín dụng/Ghi nợ',
    icon: <CardIcon />,
    description: 'Visa, Mastercard, JCB',
    processingTime: '1-2 phút',
    enabled: true
  },
  {
    id: 'bank_transfer',
    name: 'Chuyển khoản ngân hàng',
    icon: <BankIcon />,
    description: 'Chuyển khoản qua Internet Banking',
    processingTime: '5-10 phút',
    enabled: true
  },
  {
    id: 'qr_code',
    name: 'QR Code',
    icon: <QrIcon />,
    description: 'Quét mã QR bằng ví điện tử',
    processingTime: '1-3 phút',
    enabled: true
  }
];

const bankAccounts = [
  {
    bank: 'Vietcombank',
    accountNumber: '1234567890',
    accountName: 'NHAHANGTUDONG',
    branch: 'Chi nhánh Quận 1'
  },
  {
    bank: 'Techcombank', 
    accountNumber: '9876543210',
    accountName: 'NHAHANGTUDONG',
    branch: 'Chi nhánh Thủ Đức'
  }
];

const PaymentDialog: React.FC<PaymentDialogProps> = ({ 
  open, 
  onClose, 
  order, 
  onPaymentComplete 
}) => {
  const [activeStep, setActiveStep] = useState(0);
  const [selectedMethod, setSelectedMethod] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [paymentData, setPaymentData] = useState({
    cardNumber: '',
    cardExpiry: '',
    cardCvv: '',
    cardName: '',
    transferReference: '',
    notes: ''
  });
  const [timeLeft, setTimeLeft] = useState(600); // 10 minutes countdown

  const steps = ['Chọn phương thức', 'Nhập thông tin', 'Xác nhận thanh toán'];

  useEffect(() => {
    if (open && activeStep === 2 && selectedMethod !== 'cash') {
      const timer = setInterval(() => {
        setTimeLeft(prev => {
          if (prev <= 1) {
            clearInterval(timer);
            setError('Hết thời gian thanh toán. Vui lòng thử lại.');
            return 0;
          }
          return prev - 1;
        });
      }, 1000);

      return () => clearInterval(timer);
    }
  }, [open, activeStep, selectedMethod]);

  useEffect(() => {
    if (open) {
      setActiveStep(0);
      setSelectedMethod('');
      setError(null);
      setSuccess(null);
      setTimeLeft(600);
      setPaymentData({
        cardNumber: '',
        cardExpiry: '',
        cardCvv: '',
        cardName: '',
        transferReference: '',
        notes: ''
      });
    }
  }, [open]);

  const calculateTotal = () => {
    if (!order) return 0;
    return order.total_amount;
  };

  const calculateTax = () => {
    return calculateTotal() * 0.1; // 10% VAT
  };

  const handleNext = () => {
    if (activeStep === 0 && !selectedMethod) {
      setError('Vui lòng chọn phương thức thanh toán.');
      return;
    }

    if (activeStep === 1) {
      if (selectedMethod === 'card' && (!paymentData.cardNumber || !paymentData.cardExpiry || !paymentData.cardCvv || !paymentData.cardName)) {
        setError('Vui lòng nhập đầy đủ thông tin thẻ.');
        return;
      }
      if (selectedMethod === 'bank_transfer' && !paymentData.transferReference) {
        setError('Vui lòng nhập mã giao dịch chuyển khoản.');
        return;
      }
    }

    setError(null);
    setActiveStep(prev => prev + 1);
  };

  const handleBack = () => {
    setActiveStep(prev => prev - 1);
  };

  const handlePayment = async () => {
    if (!order) return;

    try {
      setLoading(true);
      setError(null);

      // Simulate payment processing
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Update order payment status
      await orderService.updateOrderStatus(order.id, 'completed');
      
      setSuccess('Thanh toán thành công!');
      
      // Call completion callback
      onPaymentComplete?.(`PAY_${Date.now()}`);

      // Close dialog after success
      setTimeout(() => {
        onClose();
      }, 2000);

    } catch (err: any) {
      console.error('Payment error:', err);
      setError('Lỗi xử lý thanh toán. Vui lòng thử lại.');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setSuccess('Đã sao chép!');
  };

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const renderPaymentMethodSelection = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Chọn phương thức thanh toán
      </Typography>
      
      <FormControl component="fieldset">
        <RadioGroup
          value={selectedMethod}
          onChange={(e) => setSelectedMethod(e.target.value)}
        >
          {paymentMethods.map((method) => (
            <Paper 
              key={method.id} 
              sx={{ 
                p: 2, 
                mb: 2, 
                border: selectedMethod === method.id ? 2 : 1,
                borderColor: selectedMethod === method.id ? 'primary.main' : 'divider',
                cursor: method.enabled ? 'pointer' : 'not-allowed',
                opacity: method.enabled ? 1 : 0.5
              }}
              onClick={() => method.enabled && setSelectedMethod(method.id)}
            >
              <FormControlLabel
                value={method.id}
                control={<Radio />}
                disabled={!method.enabled}
                label={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                    {method.icon}
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                        {method.name}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        {method.description}
                      </Typography>
                      <Typography variant="caption" color="primary">
                        Thời gian xử lý: {method.processingTime}
                      </Typography>
                    </Box>
                  </Box>
                }
                sx={{ margin: 0, width: '100%' }}
              />
            </Paper>
          ))}
        </RadioGroup>
      </FormControl>
    </Box>
  );

  const renderPaymentDetails = () => {
    switch (selectedMethod) {
      case 'cash':
        return (
          <Box>
            <Alert severity="info" sx={{ mb: 3 }}>
              Bạn đã chọn thanh toán bằng tiền mặt. Vui lòng thanh toán tại quầy khi nhận món.
            </Alert>
          </Box>
        );

      case 'card':
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Thông tin thẻ tín dụng/ghi nợ
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Số thẻ"
                  value={paymentData.cardNumber}
                  onChange={(e) => setPaymentData(prev => ({ ...prev, cardNumber: e.target.value }))}
                  placeholder="1234 5678 9012 3456"
                  inputProps={{ maxLength: 19 }}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Tên chủ thẻ"
                  value={paymentData.cardName}
                  onChange={(e) => setPaymentData(prev => ({ ...prev, cardName: e.target.value }))}
                  placeholder="NGUYEN VAN A"
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Ngày hết hạn"
                  value={paymentData.cardExpiry}
                  onChange={(e) => setPaymentData(prev => ({ ...prev, cardExpiry: e.target.value }))}
                  placeholder="MM/YY"
                  inputProps={{ maxLength: 5 }}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="CVV"
                  value={paymentData.cardCvv}
                  onChange={(e) => setPaymentData(prev => ({ ...prev, cardCvv: e.target.value }))}
                  placeholder="123"
                  inputProps={{ maxLength: 3 }}
                  type="password"
                />
              </Grid>
            </Grid>
          </Box>
        );

      case 'bank_transfer':
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Thông tin chuyển khoản
            </Typography>
            {bankAccounts.map((account, index) => (
              <Card key={index} sx={{ mb: 2 }}>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <Box>
                      <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                        {account.bank}
                      </Typography>
                      <Typography variant="body2">
                        STK: {account.accountNumber}
                      </Typography>
                      <Typography variant="body2">
                        Tên TK: {account.accountName}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        {account.branch}
                      </Typography>
                    </Box>
                    <IconButton onClick={() => copyToClipboard(account.accountNumber)}>
                      <CopyIcon />
                    </IconButton>
                  </Box>
                </CardContent>
              </Card>
            ))}
            <TextField
              fullWidth
              label="Mã giao dịch"
              value={paymentData.transferReference}
              onChange={(e) => setPaymentData(prev => ({ ...prev, transferReference: e.target.value }))}
              placeholder="Nhập mã giao dịch sau khi chuyển khoản"
              sx={{ mt: 2 }}
            />
          </Box>
        );

      case 'qr_code':
        return (
          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="h6" gutterBottom>
              Quét mã QR để thanh toán
            </Typography>
            <Paper sx={{ p: 4, display: 'inline-block', mb: 2 }}>
              <Box
                sx={{
                  width: 200,
                  height: 200,
                  bgcolor: 'grey.100',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  borderRadius: 1
                }}
              >
                <QrIcon sx={{ fontSize: 120, color: 'grey.400' }} />
              </Box>
            </Paper>
            <Typography variant="body2" color="textSecondary">
              Sử dụng ví điện tử (Momo, ZaloPay, ViettelPay) để quét mã
            </Typography>
          </Box>
        );

      default:
        return null;
    }
  };

  const renderPaymentSummary = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Xác nhận thanh toán
      </Typography>

      {/* Order Summary */}
      <Paper elevation={1} sx={{ p: 2, mb: 3 }}>
        <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 2 }}>
          Chi tiết đơn hàng
        </Typography>
        <List dense>
          {order?.items?.map((item: OrderItem, index: number) => (
            <ListItem key={index}>
              <ListItemText
                primary={`${item.dish?.name || 'Món ăn'} x${item.quantity}`}
                secondary={item.special_instructions}
              />
              <Typography variant="body2">
                {item.subtotal?.toLocaleString()}đ
              </Typography>
            </ListItem>
          ))}
        </List>
        <Divider />
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
          <Typography>Tạm tính:</Typography>
          <Typography>{calculateTotal().toLocaleString()}đ</Typography>
        </Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
          <Typography>VAT (10%):</Typography>
          <Typography>{calculateTax().toLocaleString()}đ</Typography>
        </Box>
        <Divider sx={{ my: 1 }} />
        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>Tổng cộng:</Typography>
          <Typography variant="h6" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
            {(calculateTotal() + calculateTax()).toLocaleString()}đ
          </Typography>
        </Box>
      </Paper>

      {/* Payment Method */}
      <Paper elevation={1} sx={{ p: 2, mb: 3 }}>
        <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 1 }}>
          Phương thức thanh toán
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {paymentMethods.find(m => m.id === selectedMethod)?.icon}
          <Typography>
            {paymentMethods.find(m => m.id === selectedMethod)?.name}
          </Typography>
        </Box>
      </Paper>

      {/* Timer for non-cash payments */}
      {selectedMethod !== 'cash' && (
        <Alert 
          severity={timeLeft < 60 ? "warning" : "info"} 
          icon={<TimerIcon />}
          sx={{ mb: 3 }}
        >
          Thời gian còn lại: {formatTime(timeLeft)}
        </Alert>
      )}
    </Box>
  );

  if (!order) return null;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle sx={{ bgcolor: 'primary.main', color: 'white' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <PaymentIcon />
          <Typography variant="h6">Thanh toán đơn hàng</Typography>
        </Box>
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

        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
            <CircularProgress />
          </Box>
        )}

        {activeStep === 0 && renderPaymentMethodSelection()}
        {activeStep === 1 && renderPaymentDetails()}
        {activeStep === 2 && renderPaymentSummary()}
      </DialogContent>

      <DialogActions sx={{ p: 3 }}>
        <Button onClick={onClose} disabled={loading}>
          Hủy
        </Button>
        
        {activeStep > 0 && (
          <Button onClick={handleBack} disabled={loading}>
            Quay lại
          </Button>
        )}
        
        {activeStep < steps.length - 1 ? (
          <Button variant="contained" onClick={handleNext} disabled={loading}>
            Tiếp theo
          </Button>
        ) : (
          <Button 
            variant="contained" 
            onClick={handlePayment}
            disabled={loading || timeLeft === 0}
            startIcon={loading ? <CircularProgress size={20} /> : <ConfirmIcon />}
          >
            {loading ? 'Đang xử lý...' : 'Xác nhận thanh toán'}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default PaymentDialog;