import React, { useState, useEffect, useCallback } from 'react';
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
  Typography, 
  CircularProgress, 
  Alert, 
  TablePagination,
  Grid,
  IconButton,
  Snackbar,
  Checkbox,
  FormControlLabel
} from '@mui/material';
import { 
  Add as AddIcon, 
  Edit as EditIcon, 
  Delete as DeleteIcon, 
  Search as SearchIcon,
  Clear as ClearIcon,
  Category as CategoryIcon
} from '@mui/icons-material';
import AdminLayout from '../../../components/admin/AdminLayout';
import { Category } from '../../../types';
import { categoryService } from '../../../services/admin/categoryService';

// Placeholder service - will be implemented
const AdminCategories: React.FC = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [formData, setFormData] = useState({ 
    name: '', 
    description: '',
    is_active: true
  });
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalCount, setTotalCount] = useState(0);
  
  // Filter states
  const [searchQuery, setSearchQuery] = useState('');
  const [isActiveFilter, setIsActiveFilter] = useState<string>('all');
  const [tempSearchQuery, setTempSearchQuery] = useState('');

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      const skip = page * rowsPerPage;
      const response = await categoryService.getCategories(skip, rowsPerPage, searchQuery);
      console.log('Fetched categories response:', response);
      setCategories(response.items);
      setTotalCount(response.total);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Lỗi tải dữ liệu');
    } finally {
      setLoading(false);
    }
  }, [page, rowsPerPage, searchQuery]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleSearch = () => {
    setSearchQuery(tempSearchQuery);
    setPage(0);
  };

  const handleClearSearch = () => {
    setSearchQuery('');
    setIsActiveFilter('all');
    setTempSearchQuery('');
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
    setFormData({ 
      name: '', 
      description: '',
      is_active: true
    });
    setOpenDialog(true);
  };

  const handleClose = () => {
    setOpenDialog(false);
    setEditingId(null);
  };

  const handleSave = async () => {
    if (!formData.name) {
      setError('Vui lòng điền tên danh mục');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const data = {
        name: formData.name,
        description: formData.description,
        is_active: formData.is_active,
      };

      if (editingId) {
        await categoryService.updateCategory(editingId, data);
        setSuccess('Cập nhật danh mục thành công');
      } else {
        await categoryService.createCategory(data);
        setSuccess('Thêm danh mục thành công');
      }

      await loadData();
      handleClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Lỗi lưu dữ liệu');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (item: Category) => {
    setEditingId(item.id);
    setFormData({
      name: item.name,
      description: item.description || '',
      is_active: item.is_active !== undefined ? item.is_active : true,
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
      await categoryService.deleteCategory(deletingId);
      setSuccess('Xóa danh mục thành công');
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

  if (loading && categories.length === 0) {
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
          <Typography variant="h4" sx={{ fontWeight: 'bold' }}>Quản Lý Danh Mục</Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleAddClick}
   
          >
            Thêm Danh Mục
          </Button>
        </Box>

        {/* Search and Filter Section */}
        <Card sx={{ p: 2, mb: 2 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                placeholder="Tìm kiếm theo tên danh mục..."
                value={tempSearchQuery}
                onChange={(e) => setTempSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                InputProps={{
                  endAdornment: (
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <IconButton onClick={handleSearch} size="small">
                        <SearchIcon />
                      </IconButton>
                      {(searchQuery || isActiveFilter !== 'all') && (
                        <IconButton onClick={handleClearSearch} size="small">
                          <ClearIcon />
                        </IconButton>
                      )}
                    </Box>
                  ),
                }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="body2" color="textSecondary">
                {searchQuery && `Tìm kiếm: "${searchQuery}" | `}
                Tổng cộng: {totalCount} danh mục
              </Typography>
            </Grid>
          </Grid>
        </Card>


        <Card>
          <TableContainer>
            <Table>
              <TableHead sx={{ bgcolor: '#f5f5f5' }}>
                <TableRow>
                  <TableCell sx={{ fontWeight: 'bold' }}>Tên Danh Mục</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Mô Tả</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }} align="center">Hành Động</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {categories && categories.length > 0 ? categories.map((item) => (
                  <TableRow key={item.id} hover>
                    <TableCell>

                          {item.name}
          
                    </TableCell>
                    <TableCell>{item.description || 'Không có mô tả'}</TableCell>
                    <TableCell align="center">
                      <Button size="small" startIcon={<EditIcon />} color="info" onClick={() => handleEdit(item)} sx={{ mr: 1 }}>Sửa</Button>
                      <Button size="small" startIcon={<DeleteIcon />} color="error" onClick={() => handleDelete(item.id)}>Xóa</Button>
                    </TableCell>
                  </TableRow>
                )) : (
                  <TableRow>
                    <TableCell colSpan={6} align="center" sx={{ py: 3 }}>
                      <Typography color="textSecondary">
                        {loading ? 'Đang tải...' : 'Không có danh mục nào'}
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

        {/* Add/Edit Dialog */}
        <Dialog open={openDialog} onClose={handleClose} maxWidth="md" fullWidth>
          <DialogTitle sx={{ fontWeight: 'bold', bgcolor: 'primary.main', color: 'white' }}>
            {editingId ? 'Chỉnh Sửa Danh Mục' : 'Thêm Danh Mục Mới'}
          </DialogTitle>
          <DialogContent>
            <Grid container spacing={3} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <TextField 
                    fullWidth 
                    label="Tên Danh Mục" 
                    required
                    value={formData.name} 
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })} 
                  />
                  
                  <TextField 
                    fullWidth 
                    label="Mô Tả" 
                    multiline 
                    rows={4} 
                    value={formData.description} 
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })} 
                  />

               
                </Box>
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleClose}>Hủy</Button>
            <Button onClick={handleSave} variant="contained">
              {editingId ? 'Cập Nhật' : 'Thêm Mới'}
            </Button>
          </DialogActions>
        </Dialog>

        {/* Delete Confirmation Dialog */}
        <Dialog open={openDeleteDialog} onClose={handleCancelDelete} maxWidth="sm" fullWidth>
          <DialogTitle sx={{ bgcolor: 'error.main', color: 'white', fontWeight: 'bold' }}>
            Xác nhận xóa danh mục
          </DialogTitle>
          <DialogContent sx={{ pt: 2 }}>
            <Alert severity="warning" sx={{ mb: 2 }}>
              Hành động này không thể hoàn tác. Vui lòng xác nhận để tiếp tục.
            </Alert>
            {deletingId && categories.find(item => item.id === deletingId) && (
              <Card sx={{ p: 2, bgcolor: 'grey.50' }}>
                <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
                  Danh mục sẽ bị xóa:
                </Typography>
                <Typography variant="h6" sx={{ mb: 1, fontWeight: 'bold' }}>
                  {categories.find(item => item.id === deletingId)?.name}
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

export default AdminCategories;