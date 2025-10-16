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
} from '@mui/material';
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material';
import AdminLayout from '../../../components/admin/AdminLayout';
import { tableService, Table as TableType } from '../../../services/adminService';

const AdminTables: React.FC = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [tables, setTables] = useState<TableType[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [formData, setFormData] = useState({ table_number: '', capacity: '', location: '' });
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
      const response = await tableService.getTables(skip, rowsPerPage);
      setTables(response);
      setTotalCount(500); // Giả sử có tối đa 500 bàn
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
      } else {
        await tableService.createTable(data);
      }

      await loadData();
      handleClose();
    } catch (err) {
      setError('Lỗi lưu dữ liệu');
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
    if (window.confirm('Bạn chắc chắn muốn xóa?')) {
      try {
        setLoading(true);
        await tableService.deleteTable(id);
        await loadData();
      } catch (err) {
        setError('Lỗi xóa dữ liệu');
      } finally {
        setLoading(false);
      }
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'available':
        return 'success';
      case 'occupied':
        return 'warning';
      case 'reserved':
        return 'error';
      case 'maintenance':
        return 'default';
      default:
        return 'default';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'available':
        return 'Trống';
      case 'occupied':
        return 'Đang dùng';
      case 'reserved':
        return 'Đã đặt';
      case 'maintenance':
        return 'Bảo trì';
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
          <Button variant="contained" startIcon={<AddIcon />} onClick={handleAddClick} sx={{ bgcolor: '#d32f2f' }}>Thêm Bàn</Button>
        </Box>

        {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>{error}</Alert>}

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
                {tables.map((table) => (
                  <TableRow key={table.id} hover>
                    <TableCell>{table.table_number}</TableCell>
                    <TableCell align="center">{table.capacity}</TableCell>
                    <TableCell>{table.location}</TableCell>
                    <TableCell align="center"><Chip label={getStatusLabel(table.status)} color={getStatusColor(table.status) as any} size="small" /></TableCell>
                    <TableCell align="center">
                      <Button size="small" startIcon={<EditIcon />} color="info" onClick={() => handleEdit(table)} sx={{ mr: 1 }}>Sửa</Button>
                      <Button size="small" startIcon={<DeleteIcon />} color="error" onClick={() => handleDelete(table.id)}>Xóa</Button>
                    </TableCell>
                  </TableRow>
                ))}
                {tables.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={5} align="center" sx={{ py: 3 }}>
                      <Typography color="textSecondary">Không có bàn nào</Typography>
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
          <DialogTitle>{editingId ? 'Sửa Bàn' : 'Thêm Bàn'}</DialogTitle>
          <DialogContent sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField fullWidth label="Số Bàn *" value={formData.table_number} onChange={(e) => setFormData({ ...formData, table_number: e.target.value })} />
            <TextField fullWidth label="Sức Chứa *" type="number" inputProps={{ min: '1' }} value={formData.capacity} onChange={(e) => setFormData({ ...formData, capacity: e.target.value })} />
            <TextField fullWidth label="Vị Trí" value={formData.location} onChange={(e) => setFormData({ ...formData, location: e.target.value })} />
          </DialogContent>
          <DialogActions>
            <Button onClick={handleClose}>Hủy</Button>
            <Button onClick={handleSave} variant="contained" sx={{ bgcolor: '#d32f2f' }}>{editingId ? 'Cập Nhật' : 'Thêm'}</Button>
          </DialogActions>
        </Dialog>
      </Box>
    </AdminLayout>
  );
};

export default AdminTables;