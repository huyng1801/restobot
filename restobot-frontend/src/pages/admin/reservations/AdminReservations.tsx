import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Button,
  Typography,
  CircularProgress,
  Alert,
  TablePagination,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  Snackbar,
} from '@mui/material';
import { Visibility as ViewIcon, Cancel as CancelIcon } from '@mui/icons-material';
import AdminLayout from '../../../components/admin/AdminLayout';
import { reservationService } from '../../../services/admin/reservationService';
import { Reservation } from '../../../types/adminTypes';

const AdminReservations: React.FC = () => {
  const [reservations, setReservations] = useState<Reservation[]>([]);
  const [filteredReservations, setFilteredReservations] = useState<Reservation[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalCount, setTotalCount] = useState(0);

  // Dialog states
  const [viewDialog, setViewDialog] = useState(false);
  const [cancelDialog, setCancelDialog] = useState(false);
  const [selectedReservation, setSelectedReservation] = useState<Reservation | null>(null);
  
  // Search and filter states
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [dateFilter, setDateFilter] = useState<string>('');

  useEffect(() => {
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, rowsPerPage]);

  // Filter reservations based on search term, status and date
  useEffect(() => {
    let filtered = reservations;

    // Search by customer name, email, phone or table number
    if (searchTerm) {
      filtered = filtered.filter(reservation =>
        reservation.customer_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        reservation.customer_email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        reservation.customer_phone?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        reservation.table_number?.toString().includes(searchTerm)
      );
    }

    // Filter by status
    if (statusFilter !== 'all') {
      filtered = filtered.filter(reservation => reservation.status === statusFilter);
    }

    // Filter by date
    if (dateFilter) {
      const filterDate = new Date(dateFilter).toDateString();
      filtered = filtered.filter(reservation =>
        new Date(reservation.reservation_date).toDateString() === filterDate
      );
    }

    setFilteredReservations(filtered);
    
    // Reset page when filters are applied
    if (searchTerm || statusFilter !== 'all' || dateFilter) {
      setPage(0);
    }
  }, [reservations, searchTerm, statusFilter, dateFilter]);

  const loadData = async () => {
    try {
      setLoading(true);
      const skip = page * rowsPerPage;
      const response = await reservationService.getReservations(skip, rowsPerPage);
      console.log('Fetched reservations:', response);
      setReservations(response.items);
      setTotalCount(response.total);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Lỗi tải dữ liệu');
    } finally {
      setLoading(false);
    }
  };

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleViewReservation = (reservation: Reservation) => {
    setSelectedReservation(reservation);
    setViewDialog(true);
  };

  const handleCancelClick = (reservation: Reservation) => {
    setSelectedReservation(reservation);
    setCancelDialog(true);
  };

  const handleCancelReservation = async () => {
    if (!selectedReservation) return;
    
    try {
      setLoading(true);
      await reservationService.cancelReservation(selectedReservation.id);
      setSuccess('Hủy đặt bàn thành công');
      setCancelDialog(false);
      setSelectedReservation(null);
      await loadData();
    } catch (err) {
      setError('Lỗi hủy đặt bàn');
    } finally {
      setLoading(false);
    }
  };

  // Helper function to get next status automatically
  const getNextStatus = (currentStatus: string): string | null => {
    switch (currentStatus) {
      case 'pending':
        return 'confirmed'; // Auto-transition to confirmed
      case 'confirmed':
        return 'completed'; // Auto-transition to completed
      case 'completed':
      case 'cancelled':
      case 'no_show':
        return null; // No further transitions
      default:
        return null;
    }
  };

  const handleAutoTransitionStatus = async () => {
    if (!selectedReservation) return;
    
    const nextStatus = getNextStatus(selectedReservation.status);
    if (!nextStatus) {
      setError('Không thể chuyển trạng thái từ trạng thái này');
      return;
    }
    
    try {
      setLoading(true);
      await reservationService.updateReservationStatus(selectedReservation.id, nextStatus);
      setSuccess(`Cập nhật trạng thái thành "${getStatusLabel(nextStatus)}" thành công`);
      setViewDialog(false);
      setSelectedReservation(null);
      await loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Lỗi cập nhật trạng thái');
    } finally {
      setLoading(false);
    }
  };

  const handleSpecialStatusChange = async (status: 'cancelled' | 'no_show') => {
    if (!selectedReservation) return;
    
    try {
      setLoading(true);
      await reservationService.updateReservationStatus(selectedReservation.id, status);
      setSuccess(`Cập nhật trạng thái thành "${getStatusLabel(status)}" thành công`);
      setViewDialog(false);
      setSelectedReservation(null);
      await loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Lỗi cập nhật trạng thái');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'warning';
      case 'confirmed':
        return 'success';
      case 'completed':
        return 'info';
      case 'cancelled':
        return 'error';
      case 'no_show':
        return 'default';
      default:
        return 'default';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'pending':
        return 'Chờ xác nhận';
      case 'confirmed':
        return 'Đã xác nhận';
      case 'completed':
        return 'Đã hoàn thành';
      case 'cancelled':
        return 'Đã hủy';
      case 'no_show':
        return 'Không xuất hiện';
      default:
        return status;
    }
  };

  if (loading && reservations.length === 0) {
    return (
      <AdminLayout>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
          <CircularProgress />
        </Box>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout>
      <Box>
        <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 3 }}>Quản Lý Đặt Bàn</Typography>

        {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>{error}</Alert>}

        {/* Search and Filter Section */}
        <Card sx={{ p: 2, mb: 2 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Tìm kiếm"
                placeholder="Tên khách hàng, email, SĐT, số bàn..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                variant="outlined"
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Trạng thái</InputLabel>
                <Select
                  value={statusFilter}
                  label="Trạng thái"
                  onChange={(e) => setStatusFilter(e.target.value)}
                >
                  <MenuItem value="all">Tất cả</MenuItem>
                  <MenuItem value="pending">Chờ xác nhận</MenuItem>
                  <MenuItem value="confirmed">Đã xác nhận</MenuItem>
                  <MenuItem value="completed">Đã hoàn thành</MenuItem>
                  <MenuItem value="cancelled">Đã hủy</MenuItem>
                  <MenuItem value="no_show">Không xuất hiện</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                label="Lọc theo ngày"
                type="date"
                value={dateFilter}
                onChange={(e) => setDateFilter(e.target.value)}
                variant="outlined"
                InputLabelProps={{
                  shrink: true,
                }}
              />
            </Grid>
            <Grid item xs={12} md={2}>
              <Button
                fullWidth
                variant="outlined"
                onClick={() => {
                  setSearchTerm('');
                  setStatusFilter('all');
                  setDateFilter('');
                }}
                size="small"
              >
                Xóa bộ lọc
              </Button>
            </Grid>
          </Grid>
        </Card>

        <Card>
          <TableContainer>
            <Table>
              <TableHead sx={{ bgcolor: '#f5f5f5' }}>
                <TableRow>
                  <TableCell sx={{ fontWeight: 'bold' }}>ID</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Ngày Đặt</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Khách Hàng</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Số Bàn</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }} align="center">Số Khách</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Ghi Chú</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Trạng Thái</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }} align="center">Hành Động</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {(searchTerm || statusFilter !== 'all' || dateFilter ? filteredReservations : reservations).length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} align="center" sx={{ py: 4 }}>
                      <Typography variant="body1" color="text.secondary">
                        {searchTerm || statusFilter !== 'all' || dateFilter 
                          ? 'Không tìm thấy đặt bàn phù hợp với bộ lọc' 
                          : 'Chưa có đặt bàn nào'}
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  (searchTerm || statusFilter !== 'all' || dateFilter 
                    ? filteredReservations.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                    : reservations
                  ).map((res) => (
                  <TableRow key={res.id} hover>
                    <TableCell>{res.id}</TableCell>
                    <TableCell>{new Date(res.reservation_date).toLocaleString('vi-VN')}</TableCell>
                    <TableCell>
                      <Box>
                        <Typography variant="body2" fontWeight="bold">
                          {res.customer_name}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          {res.customer_email}
                        </Typography>
                        {res.customer_phone && (
                          <Typography variant="caption" color="textSecondary" display="block">
                            {res.customer_phone}
                          </Typography>
                        )}
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box>
                        <Typography variant="body2" fontWeight="bold">
                          {res.table_number}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          Sức chứa: {res.table_capacity} người
                        </Typography>
                        {res.table_location && (
                          <Typography variant="caption" color="textSecondary" display="block">
                            Vị trí: {res.table_location}
                          </Typography>
                        )}
                      </Box>
                    </TableCell>
                    <TableCell align="center">
                      <Chip 
                        label={`${res.party_size} người`} 
                        size="small" 
                        variant="outlined" 
                        color="primary"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>
                        {res.special_requests || '-'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={getStatusLabel(res.status)}
                        color={getStatusColor(res.status) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell align="center">
                      <Button 
                        size="small" 
                        startIcon={<ViewIcon />} 
                        color="info" 
                        onClick={() => handleViewReservation(res)} 
                        sx={{ mr: 1 }}
                      >
                        Xem
                      </Button>
                      {res.status !== 'cancelled' && (
                        <Button 
                          size="small" 
                          startIcon={<CancelIcon />} 
                          color="error" 
                          onClick={() => handleCancelClick(res)}
                        >
                          Hủy
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                )))}
              </TableBody>
            </Table>
          </TableContainer>
          <TablePagination
            rowsPerPageOptions={[5, 10, 25, 50]}
            component="div"
            count={searchTerm || statusFilter !== 'all' || dateFilter ? filteredReservations.length : totalCount}
            rowsPerPage={rowsPerPage}
            page={searchTerm || statusFilter !== 'all' || dateFilter 
              ? Math.min(page, Math.max(0, Math.ceil(filteredReservations.length / rowsPerPage) - 1))
              : page
            }
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
            labelRowsPerPage="Số hàng mỗi trang:"
            labelDisplayedRows={({ from, to, count }) => `${from}-${to} của ${count !== -1 ? count : `hơn ${to}`}`}
          />
        </Card>

        {/* View Reservation Dialog */}
        <Dialog open={viewDialog} onClose={() => setViewDialog(false)} maxWidth="md" fullWidth>
          <DialogTitle sx={{ 
            bgcolor: 'primary.main', 
            color: 'white',
            display: 'flex',
            alignItems: 'center',
            gap: 1
          }}>
            <ViewIcon />
            Chi tiết đặt bàn #{selectedReservation?.id}
          </DialogTitle>
          <DialogContent>
            {selectedReservation && (
              <Box sx={{ pt: 2 }}>
                {/* Customer Info */}
                <Card sx={{ mb: 2, p: 2, bgcolor: 'grey.50' }}>
                  <Typography variant="h6" sx={{ mb: 1, color: 'primary.main' }}>
                    Thông tin khách hàng
                  </Typography>
                  <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1 }}>
                    <Typography><strong>Họ tên:</strong> {selectedReservation.customer_name}</Typography>
                    <Typography><strong>Email:</strong> {selectedReservation.customer_email}</Typography>
                    <Typography><strong>SĐT:</strong> {selectedReservation.customer_phone || 'Chưa có'}</Typography>
                  </Box>
                </Card>

                {/* Table Info */}
                <Card sx={{ mb: 2, p: 2, bgcolor: 'grey.50' }}>
                  <Typography variant="h6" sx={{ mb: 1, color: 'primary.main' }}>
                    Thông tin bàn
                  </Typography>
                  <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1 }}>
                    <Typography><strong>Số bàn:</strong> {selectedReservation.table_number}</Typography>
                    <Typography><strong>Sức chứa:</strong> {selectedReservation.table_capacity} người</Typography>
                    <Typography><strong>Vị trí:</strong> {selectedReservation.table_location || 'Không xác định'}</Typography>
                    <Typography><strong>Số khách đặt:</strong> {selectedReservation.party_size} người</Typography>
                  </Box>
                </Card>

                {/* Reservation Details */}
                <Card sx={{ mb: 2, p: 2, bgcolor: 'grey.50' }}>
                  <Typography variant="h6" sx={{ mb: 1, color: 'primary.main' }}>
                    Chi tiết đặt bàn
                  </Typography>
                  <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1 }}>
                    <Typography><strong>Ngày đặt:</strong> {new Date(selectedReservation.reservation_date).toLocaleString('vi-VN')}</Typography>
                    <Typography>
                      <strong>Trạng thái:</strong>{' '}
                      <Chip 
                        label={getStatusLabel(selectedReservation.status)} 
                        color={getStatusColor(selectedReservation.status) as any} 
                        size="small" 
                      />
                    </Typography>
                  </Box>
                  
                  {selectedReservation.special_requests && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="subtitle2" sx={{ mb: 1 }}>Yêu cầu đặc biệt:</Typography>
                      <Typography 
                        sx={{ 
                          p: 1, 
                          bgcolor: 'background.paper', 
                          border: '1px solid',
                          borderColor: 'grey.300',
                          borderRadius: 1,
                          fontStyle: 'italic'
                        }}
                      >
                        {selectedReservation.special_requests}
                      </Typography>
                    </Box>
                  )}

                  {selectedReservation.notes && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="subtitle2" sx={{ mb: 1 }}>Ghi chú nội bộ:</Typography>
                      <Typography 
                        sx={{ 
                          p: 1, 
                          bgcolor: 'warning.light', 
                          border: '1px solid',
                          borderColor: 'warning.main',
                          borderRadius: 1,
                          color: 'warning.dark'
                        }}
                      >
                        {selectedReservation.notes}
                      </Typography>
                    </Box>
                  )}
                </Card>

                {/* Status Update Section */}
                <Card sx={{ p: 2, bgcolor: 'primary.50', border: '2px solid', borderColor: 'primary.light' }}>
                  <Typography variant="h6" sx={{ mb: 2, color: 'primary.main' }}>
                    Cập Nhật Trạng Thái
                  </Typography>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                      Trạng thái hiện tại: <Chip 
                        label={getStatusLabel(selectedReservation.status)} 
                        color={getStatusColor(selectedReservation.status) as any} 
                        size="small" 
                      />
                    </Typography>
                  </Box>

                  {selectedReservation.status === 'completed' || selectedReservation.status === 'cancelled' || selectedReservation.status === 'no_show' ? (
                    <Alert severity="info">
                      Không thể cập nhật trạng thái. Đặt bàn này đã kết thúc.
                    </Alert>
                  ) : (
                    <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 2 }}>
                      {/* Auto-transition button */}
                      <Button
                        fullWidth
                        variant="contained"
                        color="primary"
                        onClick={handleAutoTransitionStatus}
                        sx={{ textTransform: 'none', fontSize: '0.95rem' }}
                      >
                        ✓ Xác Nhận Chuyển Sang {getStatusLabel(getNextStatus(selectedReservation.status) || '')}
                      </Button>

                      {/* Special status buttons */}
                      <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1 }}>
                        {selectedReservation.status === 'confirmed' && (
                          <>
                            <Button
                              variant="outlined"
                              color="warning"
                              onClick={() => handleSpecialStatusChange('no_show')}
                              sx={{ textTransform: 'none' }}
                            >
                              ⚠ Không Xuất Hiện
                            </Button>
                            <Button
                              variant="outlined"
                              color="error"
                              onClick={() => handleSpecialStatusChange('cancelled')}
                              sx={{ textTransform: 'none' }}
                            >
                              ✕ Hủy Đặt Bàn
                            </Button>
                          </>
                        )}
                        {selectedReservation.status === 'pending' && (
                          <Button
                            variant="outlined"
                            color="error"
                            onClick={() => handleSpecialStatusChange('cancelled')}
                            sx={{ textTransform: 'none', gridColumn: { xs: 'auto', md: '1 / -1' } }}
                          >
                            ✕ Hủy Đặt Bàn
                          </Button>
                        )}
                      </Box>
                    </Box>
                  )}
                </Card>
              </Box>
            )}
          </DialogContent>
          <DialogActions sx={{ p: 2, bgcolor: 'grey.100' }}>
            <Button onClick={() => setViewDialog(false)} variant="outlined">
              Đóng
            </Button>
          </DialogActions>
        </Dialog>

        {/* Cancel Confirmation Dialog */}
        <Dialog open={cancelDialog} onClose={() => setCancelDialog(false)} maxWidth="sm" fullWidth>
          <DialogTitle sx={{ 
            bgcolor: 'error.main', 
            color: 'white',
            display: 'flex',
            alignItems: 'center',
            gap: 1
          }}>
            <CancelIcon />
            Xác nhận hủy đặt bàn
          </DialogTitle>
          <DialogContent>
            <Box sx={{ pt: 2 }}>
              <Alert severity="warning" sx={{ mb: 2 }}>
                Bạn có chắc chắn muốn hủy đặt bàn này không? Hành động này không thể hoàn tác.
              </Alert>
              
              {selectedReservation && (
                <Card sx={{ p: 2, bgcolor: 'grey.50' }}>
                  <Typography variant="h6" sx={{ mb: 2, color: 'error.main' }}>
                    Thông tin đặt bàn cần hủy:
                  </Typography>
                  <Box sx={{ display: 'grid', gap: 1 }}>
                    <Typography><strong>Mã đặt bàn:</strong> #{selectedReservation.id}</Typography>
                    <Typography><strong>Khách hàng:</strong> {selectedReservation.customer_name}</Typography>
                    <Typography><strong>Số bàn:</strong> {selectedReservation.table_number}</Typography>
                    <Typography><strong>Ngày đặt:</strong> {new Date(selectedReservation.reservation_date).toLocaleString('vi-VN')}</Typography>
                    <Typography><strong>Số khách:</strong> {selectedReservation.party_size} người</Typography>
                    <Typography>
                      <strong>Trạng thái hiện tại:</strong>{' '}
                      <Chip 
                        label={getStatusLabel(selectedReservation.status)} 
                        color={getStatusColor(selectedReservation.status) as any} 
                        size="small" 
                      />
                    </Typography>
                  </Box>
                </Card>
              )}
            </Box>
          </DialogContent>
          <DialogActions sx={{ p: 2, bgcolor: 'grey.100', gap: 1 }}>
            <Button 
              onClick={() => setCancelDialog(false)} 
              variant="outlined" 
              color="inherit"
            >
              Không hủy
            </Button>
            <Button 
              onClick={handleCancelReservation} 
              color="error" 
              variant="contained"
              startIcon={<CancelIcon />}
            >
              Xác nhận hủy
            </Button>
          </DialogActions>
        </Dialog>

        {/* Success Snackbar */}
        <Snackbar
          open={!!success}
          autoHideDuration={3000}
          onClose={() => setSuccess(null)}
          anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
        >
          <Alert onClose={() => setSuccess(null)} severity="success" sx={{ width: '100%' }}>
            {success}
          </Alert>
        </Snackbar>

        {/* Error Snackbar */}
        <Snackbar
          open={!!error}
          autoHideDuration={5000}
          onClose={() => setError(null)}
          anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
        >
          <Alert onClose={() => setError(null)} severity="error" sx={{ width: '100%' }}>
            {error}
          </Alert>
        </Snackbar>
      </Box>
    </AdminLayout>
  );
};

export default AdminReservations;