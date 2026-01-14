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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Divider,
  Snackbar,
  TextField,
  Grid,
  IconButton,
  Avatar,
} from '@mui/material';
import { 
  Visibility as ViewIcon,
  Search as SearchIcon,
  Clear as ClearIcon,
  Restaurant as RestaurantIcon
} from '@mui/icons-material';
import AdminLayout from '../../../components/admin/AdminLayout';
import { orderService, Order, OrderStatus } from '../../../services/admin';

// Placeholder image for menu items without image
const getMenuImageSrc = (imageUrl?: string) => {
  if (!imageUrl) return '/api/placeholder/400/300';
  
  // Check if it's a valid base64 data URL
  if (imageUrl.startsWith('data:image/')) {
    return imageUrl;
  }
  
  // For other URLs, we could add more validation here
  // For now, return the URL or placeholder if invalid
  try {
    new URL(imageUrl);
    return imageUrl;
  } catch {
    return '/api/placeholder/400/300';
  }
};

const AdminOrders: React.FC = () => {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalCount, setTotalCount] = useState(0);
  
  // Search states
  const [searchQuery, setSearchQuery] = useState('');
  const [tempSearchQuery, setTempSearchQuery] = useState('');
  
  // Detail Modal states
  const [openDetailModal, setOpenDetailModal] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const [newStatus, setNewStatus] = useState<OrderStatus | ''>('');

  useEffect(() => {
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [statusFilter, page, rowsPerPage, searchQuery]);

  const loadData = async () => {
    try {
      setLoading(true);
      const skip = page * rowsPerPage;
      const response = await orderService.getOrders(
        skip, 
        rowsPerPage,
        statusFilter || undefined,
        searchQuery || undefined
      );
      
      setOrders(response ? response.items : []);
      setTotalCount(response ? response.total : 0);
      setError(null);
    } catch (err: any) {
      console.error('Error loading orders:', err);
      setOrders([]);
      setTotalCount(0);
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

  const handleViewDetails = async (order: Order) => {
    try {
      setLoading(true);
      const orderDetails = await orderService.getOrderDetails(order.id);
      setSelectedOrder(orderDetails);
      setNewStatus(orderDetails.status);
      setOpenDetailModal(true);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Lỗi tải chi tiết đơn hàng');
    } finally {
      setLoading(false);
    }
  };

  const handleCloseDetailModal = () => {
    setOpenDetailModal(false);
    setSelectedOrder(null);
    setNewStatus('');
  };

  const handleUpdateStatus = async () => {
    if (!selectedOrder || !newStatus) return;
    
    try {
      setLoading(true);
      await orderService.updateOrderStatus(selectedOrder.id, newStatus);
      setSuccess('Cập nhật trạng thái đơn hàng thành công');
      await loadData();
      handleCloseDetailModal();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Lỗi cập nhật trạng thái');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    setSearchQuery(tempSearchQuery);
    setPage(0);
  };

  const handleClearSearch = () => {
    setTempSearchQuery('');
    setSearchQuery('');
    setStatusFilter('');
    setPage(0);
  };

  const getCustomerDisplay = (order: Order) => {
    if (order.customer_name) return order.customer_name;
    if (order.customer_email) return order.customer_email;
    return 'Khách vãng lai';
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





  const getAvailableStatuses = (currentStatus: string) => {
    const allStatuses = [
      { value: 'pending', label: 'Chờ xử lý' },
      { value: 'confirmed', label: 'Đã xác nhận' },
      { value: 'preparing', label: 'Đang chuẩn bị' },
      { value: 'ready', label: 'Sẵn sàng' },
      { value: 'served', label: 'Đã phục vụ' },
      { value: 'completed', label: 'Hoàn thành' },
      { value: 'cancelled', label: 'Đã hủy' }
    ];

    switch (currentStatus) {
      case 'pending':
        return [
          { value: 'confirmed', label: 'Xác nhận đơn hàng' },
          { value: 'cancelled', label: 'Hủy đơn hàng' }
        ];
      case 'confirmed':
        return [
          { value: 'preparing', label: 'Bắt đầu chuẩn bị' },
          { value: 'cancelled', label: 'Hủy đơn hàng' }
        ];
      case 'preparing':
        return [
          { value: 'ready', label: 'Món đã sẵn sàng' },
          { value: 'cancelled', label: 'Hủy đơn hàng' }
        ];
      case 'ready':
        return [
          { value: 'served', label: 'Đã phục vụ khách' }
        ];
      case 'served':
        return [
          { value: 'completed', label: 'Hoàn thành đơn hàng' }
        ];
      case 'completed':
      case 'cancelled':
        return []; // No status changes allowed
      default:
        return allStatuses.filter(s => s.value !== currentStatus);
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
        </Box>

        {/* Search and Filter Section */}
        <Card sx={{ mb: 3, p: 2 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                placeholder="Tìm kiếm theo mã đơn, khách hàng..."
                value={tempSearchQuery}
                onChange={(e) => setTempSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                InputProps={{
                  endAdornment: (
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <IconButton onClick={handleSearch} size="small">
                        <SearchIcon />
                      </IconButton>
                      {(searchQuery || statusFilter) && (
                        <IconButton onClick={handleClearSearch} size="small">
                          <ClearIcon />
                        </IconButton>
                      )}
                    </Box>
                  ),
                }}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Lọc theo trạng thái</InputLabel>
                <Select
                  value={statusFilter}
                  label="Lọc theo trạng thái"
                  onChange={(e) => setStatusFilter(e.target.value)}
                >
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
            </Grid>
            <Grid item xs={12} md={5}>
              <Typography variant="body2" color="textSecondary">
                {searchQuery && `Tìm kiếm: "${searchQuery}" | `}
                {statusFilter && `Trạng thái: ${getStatusLabel(statusFilter)} | `}
                Tổng cộng: {totalCount} đơn hàng
              </Typography>
            </Grid>
          </Grid>
        </Card>

        <Card>
          <TableContainer>
            <Table>
              <TableHead sx={{ bgcolor: '#f5f5f5' }}>
                <TableRow>
                  <TableCell sx={{ fontWeight: 'bold' }}>Mã Đơn</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Khách Hàng</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Số Bàn</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }} align="right">Tổng Tiền</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Trạng Thái</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Thanh Toán</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Ngày Tạo</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }} align="center">Hành Động</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {orders && orders.length > 0 ? orders.map((order) => (
                  <TableRow key={order.id} hover>
                    <TableCell sx={{ fontWeight: 'bold' }}>{order.order_number}</TableCell>
                    <TableCell>{getCustomerDisplay(order)}</TableCell>
                    <TableCell>{order.table_number || (order.table_id ? `Bàn ${order.table_id}` : 'Mang về')}</TableCell>
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
                      <Button 
                        size="small" 
                        startIcon={<ViewIcon />} 
                        color="info"
                        onClick={() => handleViewDetails(order)}
                      >
                        Chi Tiết
                      </Button>
                    </TableCell>
                  </TableRow>
                )) : (
                  <TableRow>
                    <TableCell colSpan={8} align="center" sx={{ py: 3 }}>
                      <Typography color="textSecondary">
                        {loading ? 'Đang tải...' : 'Không có đơn hàng nào'}
                      </Typography>
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

        {/* Order Detail Modal */}
        <Dialog open={openDetailModal} onClose={handleCloseDetailModal} maxWidth="md" fullWidth>
          <DialogTitle>Chi Tiết Đơn Hàng #{selectedOrder?.order_number}</DialogTitle>
          <DialogContent sx={{ pt: 2 }}>
            {selectedOrder && (
              <Box>
                {/* Order Info */}
                <Typography variant="h6" sx={{ mb: 2 }}>Thông Tin Đơn Hàng</Typography>
                <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2, mb: 3 }}>
                  <Box>
                    <Typography variant="body2" color="textSecondary">Khách hàng:</Typography>
                    <Typography variant="body1">{getCustomerDisplay(selectedOrder)}</Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2" color="textSecondary">Số bàn:</Typography>
                    <Typography variant="body1">{selectedOrder.table_number || (selectedOrder.table_id ? `Bàn ${selectedOrder.table_id}` : 'Mang về')}</Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2" color="textSecondary">Tổng tiền:</Typography>
                    <Typography variant="body1" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                      {selectedOrder.total_amount.toLocaleString()}đ
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2" color="textSecondary">Thanh toán:</Typography>
                    <Chip
                      label={selectedOrder.payment_status === 'paid' ? 'Đã thanh toán' : 'Chưa thanh toán'}
                      color={selectedOrder.payment_status === 'paid' ? 'success' : 'warning'}
                      size="small"
                    />
                  </Box>
                  <Box>
                    <Typography variant="body2" color="textSecondary">Ngày tạo:</Typography>
                    <Typography variant="body1">{new Date(selectedOrder.created_at).toLocaleString('vi-VN')}</Typography>
                  </Box>
                </Box>

                <Divider sx={{ my: 2 }} />

                {/* Order Items */}
                <Typography variant="h6" sx={{ mb: 2 }}>Chi Tiết Món Ăn</Typography>
                {selectedOrder.order_items && selectedOrder.order_items.length > 0 ? (
                  <Box>
                    {selectedOrder.order_items.map((item, index) => (
                      <Card key={index} sx={{ mb: 2, p: 2 }}>
                        <Box sx={{ display: 'flex', gap: 2 }}>
                          {/* Item Image */}
                          <Avatar
                            src={getMenuImageSrc(item.item_image)}
                            alt={item.item_name || 'Món ăn'}
                            sx={{ width: 80, height: 80, flexShrink: 0 }}
                            variant="rounded"
                          >
                            <RestaurantIcon sx={{ fontSize: 40 }} />
                          </Avatar>
                          
                          {/* Item Details */}
                          <Box sx={{ flex: 1 }}>
                            <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                              {item.item_name || `Món ${item.menu_item_id}`}
                            </Typography>
                            <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                              Đơn giá: {item.unit_price?.toLocaleString() || item.item_price?.toLocaleString() || 'N/A'}đ
                            </Typography>
                            <Typography variant="body2" sx={{ mb: 1 }}>
                              Số lượng: {item.quantity}
                            </Typography>
                            <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                              Thành tiền: {item.total_price?.toLocaleString() || (item.quantity * (item.unit_price || item.item_price || 0)).toLocaleString()}đ
                            </Typography>
                            {item.special_instructions && (
                              <Typography variant="body2" color="textSecondary" sx={{ mt: 1, fontStyle: 'italic' }}>
                                Ghi chú: {item.special_instructions}
                              </Typography>
                            )}
                          </Box>
                        </Box>
                      </Card>
                    ))}
                  </Box>
                ) : (
                  <Typography color="textSecondary">Không có thông tin chi tiết món ăn</Typography>
                )}

                <Divider sx={{ my: 2 }} />

                {/* Order Total */}
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', p: 2, bgcolor: 'grey.50', borderRadius: 2, mb: 2 }}>
                  <Typography variant="h6">Tổng cộng:</Typography>
                  <Typography variant="h5" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                    {selectedOrder.total_amount?.toLocaleString() || 'N/A'}đ
                  </Typography>
                </Box>

                <Divider sx={{ my: 2 }} />

                {/* Status Update */}
                <Typography variant="h6" sx={{ mb: 2 }}>Cập Nhật Trạng Thái</Typography>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                    Trạng thái hiện tại: 
                    <Chip 
                      label={getStatusLabel(selectedOrder.status)} 
                      color={getStatusColor(selectedOrder.status) as any}
                      size="small"
                      sx={{ ml: 1 }}
                    />
                  </Typography>
                </Box>
                {getAvailableStatuses(selectedOrder.status).length > 0 ? (
                  <FormControl fullWidth sx={{ mb: 2 }}>
                    <InputLabel>Chọn trạng thái mới</InputLabel>
                    <Select
                      value={newStatus}
                      label="Chọn trạng thái mới"
                      onChange={(e) => setNewStatus(e.target.value as OrderStatus)}
                    >
                      {getAvailableStatuses(selectedOrder.status).map((status) => (
                        <MuiMenuItem key={status.value} value={status.value}>
                          {status.label}
                        </MuiMenuItem>
                      ))}
                    </Select>
                  </FormControl>
                ) : (
                  <Typography variant="body2" color="textSecondary" sx={{ fontStyle: 'italic', mb: 2 }}>
                    Đơn hàng đã ở trạng thái cuối, không thể thay đổi thêm.
                  </Typography>
                )}
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDetailModal}>Đóng</Button>
            {selectedOrder && getAvailableStatuses(selectedOrder.status).length > 0 && (
              <Button 
                onClick={handleUpdateStatus} 
                variant="contained" 
                disabled={!newStatus || newStatus === selectedOrder?.status}
                color={newStatus === 'cancelled' ? 'error' : 'primary'}
              >
                Cập Nhật Trạng Thái
              </Button>
            )}
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

export default AdminOrders;