import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Typography,
  CircularProgress,
  Alert,
  TablePagination,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Switch,
  FormControlLabel,
  IconButton,
  Snackbar,
} from '@mui/material';
import { 
  Add as AddIcon, 
  Edit as EditIcon, 
  Delete as DeleteIcon, 
  Search as SearchIcon,
  Clear as ClearIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon
} from '@mui/icons-material';
import AdminLayout from '../../../components/admin/AdminLayout';
import { tableService, Table as TableType, TableStatus } from '../../../services/admin';

const AdminTables: React.FC = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  const [tables, setTables] = useState<TableType[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [formData, setFormData] = useState({ table_number: '', capacity: '', location: '' });
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalCount, setTotalCount] = useState(500);
  
  // Filter states
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<TableStatus | ''>('');
  const [tempSearchQuery, setTempSearchQuery] = useState('');

  useEffect(() => {
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, rowsPerPage, searchQuery, statusFilter]);

  const loadData = async () => {
    try {
      setLoading(true);
      const skip = page * rowsPerPage;
      const response = await tableService.getTables(
        skip, 
        rowsPerPage, 
        statusFilter || undefined, 
        searchQuery || undefined
      );
   
      // Handle both old API format (array) and new API format (object with tables and total)
      if (Array.isArray(response)) {
        // Old format - direct array
        setTables(response);
       
      } else if (response && response.tables) {
        // New format - object with tables and total
        setTables(response.tables || []);
        setTotalCount(response.total || 0);
      } else {
        // Fallback - empty array
        setTables([]);
        setTotalCount(0);
      }
      
      setError(null);
    } catch (err: any) {
      console.error('Error loading tables:', err);
      setTables([]); // Set empty array on error
      setTotalCount(0);
      setError(err.response?.data?.detail || 'Lỗi tải dữ liệu');
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

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleAddClick = () => {
    setEditingId(null);
    setFormData({ table_number: '', capacity: '', location: '' });
    setOpenDialog(true);
  };

  const handleClose = () => {
    setOpenDialog(false);
    setEditingId(null);
  };

  const handleSave = async () => {
    if (!formData.table_number || !formData.capacity) {
      setError('Vui lòng điền đầy đủ thông tin');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = {
        table_number: formData.table_number,
        capacity: Number(formData.capacity),
        location: formData.location,
      };

      if (editingId) {
        await tableService.updateTable(editingId, data);
        setSuccess('Cập nhật bàn thành công');
      } else {
        await tableService.createTable(data);
        setSuccess('Thêm bàn thành công');
      }

      await loadData();
      handleClose();
    } catch (err: any) {
      if (err.response?.data?.detail?.includes('already exists')) {
        setError('Số bàn này đã tồn tại. Vui lòng chọn số khác.');
      } else {
        setError(err.response?.data?.detail || 'Lỗi lưu dữ liệu');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (table: TableType) => {
    setEditingId(table.id);
    setFormData({
      table_number: table.table_number,
      capacity: String(table.capacity),
      location: table.location || '',
    });
    setOpenDialog(true);
  };

  const handleDelete = async (id: number) => {
    setDeletingId(id);
    setOpenDeleteDialog(true);
  };

  const handleConfirmDelete = async () => {
    if (!deletingId) return;
    
    try {
      setLoading(true);
      await tableService.deleteTable(deletingId);
      setSuccess('Xóa bàn thành công');
      await loadData();
      setOpenDeleteDialog(false);
      setDeletingId(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Lỗi xóa dữ liệu');
    } finally {
      setLoading(false);
    }
  };

  const handleCancelDelete = () => {
    setOpenDeleteDialog(false);
    setDeletingId(null);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case TableStatus.AVAILABLE:
        return 'success';
      case TableStatus.OCCUPIED:
        return 'warning';
      case TableStatus.RESERVED:
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case TableStatus.AVAILABLE:
        return 'Trống';
      case TableStatus.OCCUPIED:
        return 'Đang dùng';
      case TableStatus.RESERVED:
        return 'Đã đặt';
      default:
        return status;
    }
  };

  if (loading) {
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
          <Typography variant="h4" sx={{ fontWeight: 'bold' }}>Quản Lý Bàn</Typography>
          <Button variant="contained" startIcon={<AddIcon />} onClick={handleAddClick}>Thêm Bàn</Button>
        </Box>

        {/* Search and Filter Section */}
        <Card sx={{ mb: 3, p: 2 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                placeholder="Tìm kiếm theo số bàn hoặc vị trí..."
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
                  onChange={(e) => setStatusFilter(e.target.value as TableStatus | '')}
                >
                  <MenuItem value="">Tất cả</MenuItem>
                  <MenuItem value={TableStatus.AVAILABLE}>Trống</MenuItem>
                  <MenuItem value={TableStatus.OCCUPIED}>Đang dùng</MenuItem>
                  <MenuItem value={TableStatus.RESERVED}>Đã đặt</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={5}>
              <Typography variant="body2" color="textSecondary">
                {searchQuery && `Tìm kiếm: "${searchQuery}" | `}
                {statusFilter && `Trạng thái: ${getStatusLabel(statusFilter)} | `}
                Tổng cộng: {totalCount} bàn
              </Typography>
            </Grid>
          </Grid>
        </Card>


        <Card>
          <TableContainer>
            <Table>
              <TableHead sx={{ bgcolor: '#f5f5f5' }}>
                <TableRow>
                  <TableCell sx={{ fontWeight: 'bold' }}>Số Bàn</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }} align="center">Sức Chứa</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Vị Trí</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }} align="center">Trạng Thái</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }} align="center">Hành Động</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {tables && tables.length > 0 ? tables.map((table) => (
                  <TableRow key={table.id} hover>
                    <TableCell>{table.table_number}</TableCell>
                    <TableCell align="center">{table.capacity}</TableCell>
                    <TableCell>{table.location}</TableCell>
                    <TableCell align="center">
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
                        <Chip 
                          label={getStatusLabel(table.status)} 
                          color={getStatusColor(table.status) as any} 
                          size="small" 
                        />
                      </Box>
                    </TableCell>
                    <TableCell align="center">
                      <Button size="small" startIcon={<EditIcon />} color="info" onClick={() => handleEdit(table)} sx={{ mr: 1 }}>Sửa</Button>
                      <Button size="small" startIcon={<DeleteIcon />} color="error" onClick={() => handleDelete(table.id)}>Xóa</Button>
                    </TableCell>
                  </TableRow>
                )) : (
                  <TableRow>
                    <TableCell colSpan={5} align="center" sx={{ py: 3 }}>
                      <Typography color="textSecondary">
                        {loading ? 'Đang tải...' : 'Không có bàn nào'}
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

        <Dialog open={openDialog} onClose={handleClose} maxWidth="sm" fullWidth>
          <DialogTitle sx={{ fontWeight: 'bold', bgcolor: 'primary.main', color: 'white' }}>{editingId ? 'Sửa Bàn' : 'Thêm Bàn'}</DialogTitle>
          <DialogContent sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 2, mt: 3, overflowY: 'visible' }}>
            <TextField fullWidth label="Số Bàn *" value={formData.table_number} onChange={(e) => setFormData({ ...formData, table_number: e.target.value })} />
            <TextField fullWidth label="Sức Chứa *" type="number" inputProps={{ min: '1' }} value={formData.capacity} onChange={(e) => setFormData({ ...formData, capacity: e.target.value })} />
            <TextField fullWidth label="Vị Trí" value={formData.location} onChange={(e) => setFormData({ ...formData, location: e.target.value })} />
          </DialogContent>
          <DialogActions>
            <Button onClick={handleClose}>Hủy</Button>
            <Button onClick={handleSave} variant="contained" sx={{ bgcolor: '#d32f2f' }}>{editingId ? 'Cập Nhật' : 'Thêm'}</Button>
          </DialogActions>
        </Dialog>

        {/* Delete Confirmation Dialog */}
    {/* Delete Confirmation Dialog */}
        <Dialog open={openDeleteDialog} onClose={handleCancelDelete} maxWidth="sm" fullWidth>
          <DialogTitle sx={{ bgcolor: 'error.main', color: 'white', fontWeight: 'bold' }}>
            Xác nhận xóa bàn
          </DialogTitle>
          <DialogContent sx={{ pt: 2 }}>
            <Alert severity="warning" sx={{ mb: 2 }}>
              Hành động này không thể hoàn tác. Vui lòng xác nhận để tiếp tục.
            </Alert>
            {deletingId && tables.find(item => item.id === deletingId) && (
              <Card sx={{ p: 2, bgcolor: 'grey.50' }}>
                <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
                  Bàn sẽ bị xóa:
                </Typography>
                <Typography variant="h6" sx={{ mb: 1, fontWeight: 'bold' }}>
                  {tables.find(item => item.id === deletingId)?.table_number}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  Số chỗ ngồi: {tables.find(item => item.id === deletingId)?.capacity}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  ID: {deletingId}
                </Typography>
              </Card>
            )}
          </DialogContent>
          <DialogActions sx={{ p: 2, bgcolor: 'grey.100', gap: 1 }}>
            <Button onClick={handleCancelDelete} variant="outlined">
              Hủy
            </Button>
            <Button onClick={handleConfirmDelete} color="error" variant="contained">
              Xác nhận xóa
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

export default AdminTables;