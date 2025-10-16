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
  Dialog, 
  DialogTitle, 
  DialogContent, 
  DialogActions, 
  TextField, 
  Select, 
  MenuItem as MuiMenuItem, 
  FormControl, 
  InputLabel, 
  Typography, 
  CircularProgress, 
  Alert, 
  Chip, 
  TablePagination 
} from '@mui/material';
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material';
import AdminLayout from '../../../components/admin/AdminLayout';
import { menuService, MenuItem, Category } from '../../../services/adminService';

const AdminMenu: React.FC = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [menuItems, setMenuItems] = useState<MenuItem[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [formData, setFormData] = useState({ name: '', category_id: '', price: '', description: '', preparation_time: '' });
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
      const itemsResponse = await menuService.getMenuItems(skip, rowsPerPage);
      const catsResponse = await menuService.getCategories(0, 100);
      setMenuItems(itemsResponse);
      setCategories(catsResponse);
      setTotalCount(200); // Giả sử có tối đa 200 món ăn
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
    setFormData({ name: '', category_id: '', price: '', description: '', preparation_time: '' });
    setOpenDialog(true);
  };

  const handleClose = () => {
    setOpenDialog(false);
    setEditingId(null);
  };

  const handleSave = async () => {
    if (!formData.name || !formData.category_id || !formData.price) {
      setError('Vui lòng điền đầy đủ thông tin');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = {
        name: formData.name,
        category_id: Number(formData.category_id),
        price: Number(formData.price),
        description: formData.description,
        preparation_time: formData.preparation_time ? Number(formData.preparation_time) : undefined,
      };

      if (editingId) {
        await menuService.updateMenuItem(editingId, data);
      } else {
        await menuService.createMenuItem(data);
      }

      await loadData();
      handleClose();
    } catch (err) {
      setError('Lỗi lưu dữ liệu');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (item: MenuItem) => {
    setEditingId(item.id);
    setFormData({
      name: item.name,
      category_id: String(item.category_id),
      price: String(item.price),
      description: item.description || '',
      preparation_time: String(item.preparation_time || ''),
    });
    setOpenDialog(true);
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Bạn chắc chắn muốn xóa?')) {
      try {
        setLoading(true);
        await menuService.deleteMenuItem(id);
        await loadData();
      } catch (err) {
        setError('Lỗi xóa dữ liệu');
      } finally {
        setLoading(false);
      }
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
          <Typography variant="h4" sx={{ fontWeight: 'bold' }}>Quản Lý Thực Đơn</Typography>
          <Button variant="contained" startIcon={<AddIcon />} onClick={handleAddClick} sx={{ bgcolor: '#d32f2f' }}>Thêm Món</Button>
        </Box>

        {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>{error}</Alert>}

        <Card>
          <TableContainer>
            <Table>
              <TableHead sx={{ bgcolor: '#f5f5f5' }}>
                <TableRow>
                  <TableCell sx={{ fontWeight: 'bold' }}>Tên Món</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Danh Mục</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }} align="right">Giá</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Mô Tả</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }} align="center">Trạng Thái</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }} align="center">Hành Động</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {menuItems.map((item) => (
                  <TableRow key={item.id} hover>
                    <TableCell>{item.name}</TableCell>
                    <TableCell>{item.category_id}</TableCell>
                    <TableCell align="right">{item.price.toLocaleString()}đ</TableCell>
                    <TableCell>{item.description}</TableCell>
                    <TableCell align="center"><Chip label={item.is_available ? 'Sẵn' : 'Hết'} color={item.is_available ? 'success' : 'error'} size="small" /></TableCell>
                    <TableCell align="center">
                      <Button size="small" startIcon={<EditIcon />} color="info" onClick={() => handleEdit(item)} sx={{ mr: 1 }}>Sửa</Button>
                      <Button size="small" startIcon={<DeleteIcon />} color="error" onClick={() => handleDelete(item.id)}>Xóa</Button>
                    </TableCell>
                  </TableRow>
                ))}
                {menuItems.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={6} align="center" sx={{ py: 3 }}>
                      <Typography color="textSecondary">Không có món ăn nào</Typography>
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
          <DialogTitle>{editingId ? 'Sửa Món Ăn' : 'Thêm Món Ăn'}</DialogTitle>
          <DialogContent sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField fullWidth label="Tên Món *" value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} />
            <FormControl fullWidth>
              <InputLabel>Danh Mục *</InputLabel>
              <Select value={formData.category_id} label="Danh Mục *" onChange={(e) => setFormData({ ...formData, category_id: e.target.value })}>
                {categories.map((cat) => (<MuiMenuItem key={cat.id} value={cat.id}>{cat.name}</MuiMenuItem>))}
              </Select>
            </FormControl>
            <TextField fullWidth label="Giá *" type="number" inputProps={{ step: '1000' }} value={formData.price} onChange={(e) => setFormData({ ...formData, price: e.target.value })} />
            <TextField fullWidth label="Thời Gian Chuẩn Bị (phút)" type="number" value={formData.preparation_time} onChange={(e) => setFormData({ ...formData, preparation_time: e.target.value })} />
            <TextField fullWidth label="Mô Tả" multiline rows={3} value={formData.description} onChange={(e) => setFormData({ ...formData, description: e.target.value })} />
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

export default AdminMenu;
