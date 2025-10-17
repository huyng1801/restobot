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
  TablePagination,
  Grid,
  IconButton,
  Snackbar,
  Avatar,
  Checkbox,
  FormControlLabel
} from '@mui/material';
import { 
  Add as AddIcon, 
  Edit as EditIcon, 
  Delete as DeleteIcon, 
  Search as SearchIcon,
  Clear as ClearIcon,
  PhotoCamera as PhotoCameraIcon,
  Restaurant as RestaurantIcon,
  Close as CloseIcon
} from '@mui/icons-material';
import AdminLayout from '../../../components/admin/AdminLayout';
import { menuService, MenuItem, Category } from '../../../services/admin';

// Utility function to validate image size in base64
const getBase64ImageSize = (base64: string) => {
  const sizeInBytes = (base64.length * 3) / 4;
  return sizeInBytes / (1024 * 1024); // Convert to MB
};

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

const AdminMenu: React.FC = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  const [menuItems, setMenuItems] = useState<MenuItem[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [formData, setFormData] = useState({ 
    name: '', 
    category_id: '', 
    price: '', 
    description: '', 
    preparation_time: '', 
    image_url: '',
    is_featured: false,
    is_available: true
  });
  const [imagePreview, setImagePreview] = useState<string>('');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalCount, setTotalCount] = useState(0);
  
  // Filter states
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string>('');
  const [isFeaturedFilter, setIsFeaturedFilter] = useState<string>('all');
  const [isAvailableFilter, setIsAvailableFilter] = useState<string>('all');
  const [tempSearchQuery, setTempSearchQuery] = useState('');

  useEffect(() => {
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, rowsPerPage, searchQuery, categoryFilter, isFeaturedFilter, isAvailableFilter]);

  const loadData = async () => {
    try {
      setLoading(true);
      const skip = page * rowsPerPage;
      const categoryId = categoryFilter ? Number(categoryFilter) : undefined;
      
      // Convert filter states to booleans
      const isFeatured = isFeaturedFilter === 'true' ? true : isFeaturedFilter === 'false' ? false : undefined;
      const isAvailable = isAvailableFilter === 'true' ? true : isAvailableFilter === 'false' ? false : undefined;
      
      const itemsResponse = await menuService.getMenuItems(skip, rowsPerPage, categoryId, searchQuery || undefined, isFeatured, isAvailable);
      const catsResponse = await menuService.getCategories(0, 100);
      
      setMenuItems(itemsResponse.items || []);
      // Handle new pagination response structure for categories
      setCategories(catsResponse ? catsResponse.items : (Array.isArray(catsResponse) ? catsResponse : []));
      setTotalCount(itemsResponse.total || 0);
      console.log('Fetched menu items:', itemsResponse);
      setError(null);
    } catch (err: any) {
      console.error('Error loading menu items:', err);
      setMenuItems([]);
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

  const handleSearch = () => {
    setSearchQuery(tempSearchQuery);
    setPage(0);
  };

  const handleClearSearch = () => {
    setTempSearchQuery('');
    setSearchQuery('');
    setCategoryFilter('');
    setIsFeaturedFilter('all');
    setIsAvailableFilter('all');
    setPage(0);
  };

  const getCategoryName = (categoryId: number) => {
    const category = categories.find(cat => cat.id === categoryId);
    return category ? category.name : `ID: ${categoryId}`;
  };

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        setError('Kích thước file không được vượt quá 5MB');
        return;
      }

      // Validate file type
      if (!file.type.startsWith('image/')) {
        setError('Vui lòng chọn file hình ảnh');
        return;
      }

      const reader = new FileReader();
      reader.onload = (e) => {
        const base64Result = e.target?.result as string;
        
        // Validate base64 size (should be under 5MB after conversion)
        const sizeInMB = getBase64ImageSize(base64Result);
        if (sizeInMB > 5) {
          setError('Kích thước hình ảnh sau chuyển đổi không được vượt quá 5MB');
          return;
        }
        
        setImagePreview(base64Result);
        // Tự động cập nhật formData với base64 string
        setFormData({ ...formData, image_url: base64Result });
      };
      reader.readAsDataURL(file);
    }
  };

  const handleRemoveImage = () => {
    setImagePreview('');
    setFormData({ ...formData, image_url: '' });
    // Reset file input
    const fileInput = document.getElementById('image-upload') as HTMLInputElement;
    if (fileInput) fileInput.value = '';
  };

  const handleAddClick = () => {
    setEditingId(null);
    setFormData({ 
      name: '', 
      category_id: '', 
      price: '', 
      description: '', 
      preparation_time: '', 
      image_url: '',
      is_featured: false,
      is_available: true
    });
    setImagePreview('');
    setOpenDialog(true);
  };

  const handleClose = () => {
    setOpenDialog(false);
    setEditingId(null);
    setImagePreview('');
    // Reset file input
    const fileInput = document.getElementById('image-upload') as HTMLInputElement;
    if (fileInput) fileInput.value = '';
  };

  const handleSave = async () => {
    if (!formData.name || !formData.category_id || !formData.price) {
      setError('Vui lòng điền đầy đủ thông tin');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      // Use base64 string directly from formData (already set when image is uploaded)
      const data = {
        name: formData.name,
        category_id: Number(formData.category_id),
        price: Number(formData.price),
        description: formData.description,
        preparation_time: formData.preparation_time ? Number(formData.preparation_time) : undefined,
        image_url: formData.image_url || undefined,
        is_featured: formData.is_featured,
        is_available: formData.is_available,
      };

      if (editingId) {
        await menuService.updateMenuItem(editingId, data);
        setSuccess('Cập nhật món ăn thành công');
      } else {
        await menuService.createMenuItem(data);
        setSuccess('Thêm món ăn thành công');
      }

      await loadData();
      handleClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Lỗi lưu dữ liệu');
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
      image_url: item.image_url || '',
      is_featured: item.is_featured || false,
      is_available: item.is_available !== undefined ? item.is_available : true,
    });
 
    setImagePreview(item.image_url || '');
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
      await menuService.deleteMenuItem(deletingId);
      setSuccess('Xóa món ăn thành công');
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
          <Button variant="contained" startIcon={<AddIcon />} onClick={handleAddClick}>Thêm Món</Button>
        </Box>

        {/* Search and Filter Section */}
        <Card sx={{ mb: 3, p: 2 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                placeholder="Tìm kiếm theo tên món..."
                value={tempSearchQuery}
                onChange={(e) => setTempSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                InputProps={{
                  endAdornment: (
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <IconButton onClick={handleSearch} size="small">
                        <SearchIcon />
                      </IconButton>
                      {(searchQuery || categoryFilter || isFeaturedFilter !== 'all' || isAvailableFilter !== 'all') && (
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
                <InputLabel>Lọc theo danh mục</InputLabel>
                <Select
                  value={categoryFilter}
                  label="Lọc theo danh mục"
                  onChange={(e) => setCategoryFilter(e.target.value)}
                >
                  <MuiMenuItem value="">Tất cả</MuiMenuItem>
                  {categories.map((category) => (
                    <MuiMenuItem key={category.id} value={category.id}>
                      {category.name}
                    </MuiMenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2}>
              <FormControl fullWidth>
                <InputLabel>Nổi bật</InputLabel>
                <Select
                  value={isFeaturedFilter}
                  label="Nổi bật"
                  onChange={(e) => setIsFeaturedFilter(e.target.value)}
                >
                  <MuiMenuItem value="all">Tất cả</MuiMenuItem>
                  <MuiMenuItem value="true">Nổi bật</MuiMenuItem>
                  <MuiMenuItem value="false">Thường</MuiMenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2}>
              <FormControl fullWidth>
                <InputLabel>Sẵn sàng</InputLabel>
                <Select
                  value={isAvailableFilter}
                  label="Sẵn sàng"
                  onChange={(e) => setIsAvailableFilter(e.target.value)}
                >
                  <MuiMenuItem value="all">Tất cả</MuiMenuItem>
                  <MuiMenuItem value="true">Sẵn sàng</MuiMenuItem>
                  <MuiMenuItem value="false">Ngưng bán</MuiMenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2}>
              <Button 
                fullWidth 
                variant="outlined"
                onClick={() => {
                  setSearchQuery('');
                  setTempSearchQuery('');
                  setCategoryFilter('');
                  setIsFeaturedFilter('all');
                  setIsAvailableFilter('all');
                }}
              >
                Xóa bộ lọc
              </Button>
            </Grid>
            <Grid item xs={12} md={5}>
              <Typography variant="body2" color="textSecondary">
                {searchQuery && `Tìm kiếm: "${searchQuery}" | `}
                {categoryFilter && `Danh mục: ${getCategoryName(Number(categoryFilter))} | `}
                {isFeaturedFilter !== 'all' && `Nổi bật: ${isFeaturedFilter === 'true' ? 'Có' : 'Không'} | `}
                {isAvailableFilter !== 'all' && `Sẵn sàng: ${isAvailableFilter === 'true' ? 'Có' : 'Không'} | `}
                Tổng cộng: {totalCount} món
              </Typography>
            </Grid>
          </Grid>
        </Card>

        {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>{error}</Alert>}

        <Card>
          <TableContainer>
            <Table>
              <TableHead sx={{ bgcolor: '#f5f5f5' }}>
                <TableRow>
                  <TableCell sx={{ fontWeight: 'bold' }} align="center">Hình Ảnh</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Tên Món</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Danh Mục</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }} align="right">Giá</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }} align="center">Thời Gian</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Mô Tả</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }} align="center">Nổi Bật</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }} align="center">Sẵn Sàng</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }} align="center">Hành Động</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {menuItems && menuItems.length > 0 ? menuItems.map((item) => (
                  <TableRow key={item.id} hover>
                    <TableCell align="center">
                      <Avatar
                        src={getMenuImageSrc(item.image_url)}
                        alt={item.name}
                        sx={{ width: 50, height: 50, mx: 'auto' }}
                        variant="rounded"
                      >
                        <RestaurantIcon />
                      </Avatar>
                    </TableCell>
                    <TableCell>{item.name}</TableCell>
                    <TableCell>{getCategoryName(item.category_id)}</TableCell>
                    <TableCell align="right">{item.price.toLocaleString()}đ</TableCell>
                    <TableCell align="center">
                      {item.preparation_time ? `${item.preparation_time} phút` : 'Chưa xác định'}
                    </TableCell>
                    <TableCell>{item.description || 'Không có mô tả'}</TableCell>
                    <TableCell align="center">
                      {item.is_featured ? (
                        <Checkbox checked disabled size="small" />
                      ) : (
                        <Checkbox checked={false} disabled size="small" />
                      )}
                    </TableCell>
                    <TableCell align="center">
                      {item.is_available ? (
                        <Checkbox checked disabled size="small" />
                      ) : (
                        <Checkbox checked={false} disabled size="small" />
                      )}
                    </TableCell>
                    <TableCell align="center">
                      <Button size="small" startIcon={<EditIcon />} color="info" onClick={() => handleEdit(item)} sx={{ mr: 1 }}>Sửa</Button>
                      <Button size="small" startIcon={<DeleteIcon />} color="error" onClick={() => handleDelete(item.id)}>Xóa</Button>
                    </TableCell>
                  </TableRow>
                )) : (
                  <TableRow>
                    <TableCell colSpan={9} align="center" sx={{ py: 3 }}>
                      <Typography color="textSecondary">
                        {loading ? 'Đang tải...' : 'Không có món ăn nào'}
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

        <Dialog open={openDialog} onClose={handleClose} maxWidth="md" fullWidth>
          <DialogTitle sx={{ fontWeight: 'bold', bgcolor: 'primary.main', color: 'white' }}>{editingId ? 'Sửa Món Ăn' : 'Thêm Món Ăn'}</DialogTitle>
          <DialogContent sx={{ pt: 2 }}>
            <Grid container spacing={3} sx={{ mt: 1 }}>
              {/* Image Upload Section */}
              <Grid item xs={12} md={4}>
                <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
                  <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                    Hình Ảnh Món Ăn
                  </Typography>
                  
                  {/* Image Preview */}
                  <Box
                    sx={{
                      width: 200,
                      height: 200,
                      border: '2px dashed #ccc',
                      borderRadius: 2,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      position: 'relative',
                      overflow: 'hidden',
                      bgcolor: 'grey.50'
                    }}
                  >
                    {imagePreview || formData.image_url ? (
                      <>
                        <img
                          src={imagePreview || formData.image_url}
                          alt="Preview"
                          style={{
                            width: '100%',
                            height: '100%',
                            objectFit: 'cover'
                          }}
                        />
                        <IconButton
                          onClick={handleRemoveImage}
                          sx={{
                            position: 'absolute',
                            top: 8,
                            right: 8,
                            bgcolor: 'rgba(0,0,0,0.5)',
                            color: 'white',
                            '&:hover': {
                              bgcolor: 'rgba(0,0,0,0.7)',
                            }
                          }}
                          size="small"
                        >
                          <CloseIcon />
                        </IconButton>
                      </>
                    ) : (
                      <Box sx={{ textAlign: 'center', color: 'grey.500' }}>
                        <RestaurantIcon sx={{ fontSize: 48, mb: 1 }} />
                        <Typography variant="body2">
                          Chưa có hình ảnh
                        </Typography>
                      </Box>
                    )}
                  </Box>

                  {/* Upload Button */}
                  <input
                    accept="image/*"
                    style={{ display: 'none' }}
                    id="image-upload"
                    type="file"
                    onChange={handleImageUpload}
                  />
                  <label htmlFor="image-upload">
                    <Button
                      variant="outlined"
                      component="span"
                      startIcon={<PhotoCameraIcon />}
                      fullWidth
                    >
                      Chọn Hình Ảnh
                    </Button>
                  </label>

                  {/* Image URL Input */}
                  <TextField
                    fullWidth
                    label="URL Hình Ảnh hoặc Base64"
                    placeholder="https://example.com/image.jpg hoặc data:image/..."
                    value={formData.image_url}
                    onChange={(e) => {
                      const value = e.target.value;
                      setFormData({ ...formData, image_url: value });
                      // Only update preview if it's a valid URL or base64
                      if (value.startsWith('http') || value.startsWith('data:image/')) {
                        setImagePreview(value);
                      } else if (value === '') {
                        setImagePreview('');
                      }
                    }}
                    size="small"
                    helperText="Chọn file để tự động chuyển đổi sang base64 hoặc nhập URL trực tiếp"
                  />
                </Box>
              </Grid>

              {/* Form Fields */}
              <Grid item xs={12} md={8}>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 , paddingTop: '16px'}}>
                  <TextField 
                    fullWidth 
                    label="Tên Món *" 
                    value={formData.name} 
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })} 
                  />
                  
                  <FormControl fullWidth>
                    <InputLabel>Danh Mục *</InputLabel>
                    <Select 
                      value={formData.category_id} 
                      label="Danh Mục *" 
                      onChange={(e) => setFormData({ ...formData, category_id: e.target.value })}
                    >
                      {categories.map((cat) => (
                        <MuiMenuItem key={cat.id} value={cat.id}>
                          {cat.name}
                        </MuiMenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  
                  <TextField 
                    fullWidth 
                    label="Giá *" 
                    type="number" 
                    inputProps={{ step: '1000' }} 
                    value={formData.price} 
                    onChange={(e) => setFormData({ ...formData, price: e.target.value })} 
                  />
                  
                  <TextField 
                    fullWidth 
                    label="Thời Gian Chuẩn Bị (phút)" 
                    type="number" 
                    value={formData.preparation_time} 
                    onChange={(e) => setFormData({ ...formData, preparation_time: e.target.value })} 
                  />
                  
                  <TextField 
                    fullWidth 
                    label="Mô Tả" 
                    multiline 
                    rows={4} 
                    value={formData.description} 
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })} 
                  />

                  <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={formData.is_featured}
                          onChange={(e) => setFormData({ ...formData, is_featured: e.target.checked })}
                        />
                      }
                      label="Món nổi bật"
                    />
                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={formData.is_available}
                          onChange={(e) => setFormData({ ...formData, is_available: e.target.checked })}
                        />
                      }
                      label="Sẵn sàng phục vụ"
                    />
                  </Box>
                </Box>
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleClose}>Hủy</Button>
            <Button onClick={handleSave} variant="contained">{editingId ? 'Cập Nhật' : 'Thêm'}</Button>
          </DialogActions>
        </Dialog>

        {/* Delete Confirmation Dialog */}
        <Dialog open={openDeleteDialog} onClose={handleCancelDelete} maxWidth="sm" fullWidth>
          <DialogTitle sx={{ bgcolor: 'error.main', color: 'white', fontWeight: 'bold' }}>
            Xác nhận xóa món ăn
          </DialogTitle>
          <DialogContent sx={{ pt: 2 }}>
            <Alert severity="warning" sx={{ mb: 2 }}>
              Hành động này không thể hoàn tác. Vui lòng xác nhận để tiếp tục.
            </Alert>
            {deletingId && menuItems.find(item => item.id === deletingId) && (
              <Card sx={{ p: 2, bgcolor: 'grey.50' }}>
                <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
                  Món ăn sẽ bị xóa:
                </Typography>
                <Typography variant="h6" sx={{ mb: 1, fontWeight: 'bold' }}>
                  {menuItems.find(item => item.id === deletingId)?.name}
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

export default AdminMenu;
