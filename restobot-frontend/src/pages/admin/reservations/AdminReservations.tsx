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
} from '@mui/material';
import { Visibility as ViewIcon, Cancel as CancelIcon } from '@mui/icons-material';
import AdminLayout from '../../../components/admin/AdminLayout';
import { reservationService, Reservation } from '../../../services/adminService';

const AdminReservations: React.FC = () => {
  const [reservations, setReservations] = useState<Reservation[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalCount, setTotalCount] = useState(0);

  useEffect(() => {
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, rowsPerPage]);

  const loadData = async () => {
    try {
      setLoading(true);
      const skip = page * rowsPerPage;
      const response = await reservationService.getReservations(skip, rowsPerPage);
      setReservations(response);
      setTotalCount(500); // Giả sử có tối đa 500 đặt bàn
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

  const handleCancelReservation = async (id: number) => {
    if (window.confirm('Bạn chắc chắn muốn hủy đặt bàn này?')) {
      try {
        setLoading(true);
        await reservationService.cancelReservation(id);
        await loadData();
      } catch (err) {
        setError('Lỗi hủy đặt bàn');
      } finally {
        setLoading(false);
      }
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

        <Card>
          <TableContainer>
            <Table>
              <TableHead sx={{ bgcolor: '#f5f5f5' }}>
                <TableRow>
                  <TableCell sx={{ fontWeight: 'bold' }}>Ngày Đặt</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Bàn</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }} align="center">Khách</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Ghi Chú Đặc Biệt</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Trạng Thái</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }} align="center">Hành Động</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {reservations.map((res) => (
                  <TableRow key={res.id} hover>
                    <TableCell>{new Date(res.reservation_date).toLocaleString('vi-VN')}</TableCell>
                    <TableCell>Bàn {res.table_id}</TableCell>
                    <TableCell align="center">{res.party_size}</TableCell>
                    <TableCell>{res.special_requests || '-'}</TableCell>
                    <TableCell>
                      <Chip
                        label={getStatusLabel(res.status)}
                        color={getStatusColor(res.status) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell align="center">
                      <Button size="small" startIcon={<ViewIcon />} color="info" sx={{ mr: 1 }}>Xem</Button>
                      {res.status !== 'cancelled' && (
                        <Button size="small" startIcon={<CancelIcon />} color="error" onClick={() => handleCancelReservation(res.id)}>Hủy</Button>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
                {reservations.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={6} align="center" sx={{ py: 3 }}>
                      <Typography color="textSecondary">Không có đặt bàn nào</Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
          <TablePagination
            rowsPerPageOptions={[5, 10, 25, 50]}
            component="div"
            count={totalCount}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
            labelRowsPerPage="Số hàng mỗi trang:"
            labelDisplayedRows={({ from, to, count }) => `${from}-${to} của ${count !== -1 ? count : `hơn ${to}`}`}
          />
        </Card>
      </Box>
    </AdminLayout>
  );
};

export default AdminReservations;