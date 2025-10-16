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
  Select,
  MenuItem as MuiMenuItem,
  FormControl,
  InputLabel,
  TablePagination,
} from '@mui/material';
import { Visibility as ViewIcon } from '@mui/icons-material';
import AdminLayout from '../../../components/admin/AdminLayout';
import { orderService, Order, OrderStatus } from '../../../services/adminService';

const AdminOrders: React.FC = () => {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalCount, setTotalCount] = useState(0);

  useEffect(() => {
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [statusFilter, page, rowsPerPage]);

  const loadData = async () => {
    try {
      setLoading(true);
      const skip = page * rowsPerPage;
      const response = await orderService.getOrders(skip, rowsPerPage);
      setOrders(response);
      setTotalCount(1000); // Giả sử có tối đa 1000 đơn hàng
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

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'default';
      case 'confirmed':
        return 'info';
      case 'preparing':
        return 'warning';
      case 'ready':
        return 'secondary';
      case 'served':
        return 'primary';
      case 'completed':
        return 'success';
      case 'cancelled':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'pending':
        return 'Chờ xử lý';
      case 'confirmed':
        return 'Đã xác nhận';
      case 'preparing':
        return 'Đang chuẩn bị';
      case 'ready':
        return 'Sẵn sàng';
      case 'served':
        return 'Đã phục vụ';
      case 'completed':
        return 'Hoàn thành';
      case 'cancelled':
        return 'Đã hủy';
      default:
        return status;
    }
  };

  if (loading && orders.length === 0) {
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
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" sx={{ fontWeight: 'bold' }}>Quản Lý Đơn Hàng</Typography>
          <FormControl sx={{ minWidth: 200 }}>
            <InputLabel>Lọc theo trạng thái</InputLabel>
            <Select value={statusFilter} label="Lọc theo trạng thái" onChange={(e) => setStatusFilter(e.target.value)}>
              <MuiMenuItem value="">Tất cả</MuiMenuItem>
              <MuiMenuItem value={OrderStatus.PENDING}>Chờ xử lý</MuiMenuItem>
              <MuiMenuItem value={OrderStatus.CONFIRMED}>Đã xác nhận</MuiMenuItem>
              <MuiMenuItem value={OrderStatus.PREPARING}>Đang chuẩn bị</MuiMenuItem>
              <MuiMenuItem value={OrderStatus.READY}>Sẵn sàng</MuiMenuItem>
              <MuiMenuItem value={OrderStatus.SERVED}>Đã phục vụ</MuiMenuItem>
              <MuiMenuItem value={OrderStatus.COMPLETED}>Hoàn thành</MuiMenuItem>
              <MuiMenuItem value={OrderStatus.CANCELLED}>Đã hủy</MuiMenuItem>
            </Select>
          </FormControl>
        </Box>

        {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>{error}</Alert>}

        <Card>
          <TableContainer>
            <Table>
              <TableHead sx={{ bgcolor: '#f5f5f5' }}>
                <TableRow>
                  <TableCell sx={{ fontWeight: 'bold' }}>Mã Đơn</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }} align="right">Tổng Tiền</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Trạng Thái</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Trạng Thái Thanh Toán</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Ngày Tạo</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }} align="center">Hành Động</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {orders.map((order) => (
                  <TableRow key={order.id} hover>
                    <TableCell sx={{ fontWeight: 'bold' }}>{order.order_number}</TableCell>
                    <TableCell align="right">{order.total_amount.toLocaleString()}đ</TableCell>
                    <TableCell>
                      <Chip
                        label={getStatusLabel(order.status)}
                        color={getStatusColor(order.status) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={order.payment_status === 'paid' ? 'Đã thanh toán' : 'Chưa thanh toán'}
                        color={order.payment_status === 'paid' ? 'success' : 'warning'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{new Date(order.created_at).toLocaleString('vi-VN')}</TableCell>
                    <TableCell align="center">
                      <Button size="small" startIcon={<ViewIcon />} color="info">Xem Chi Tiết</Button>
                    </TableCell>
                  </TableRow>
                ))}
                {orders.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={6} align="center" sx={{ py: 3 }}>
                      <Typography color="textSecondary">Không có đơn hàng nào</Typography>
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

export default AdminOrders;