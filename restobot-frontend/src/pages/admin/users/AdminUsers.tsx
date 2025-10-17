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
  Paper,
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
  TextField,
  Grid,
  IconButton,
  Snackbar,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Search as SearchIcon,
  Clear as ClearIcon,
} from '@mui/icons-material';
import AdminLayout from '../../../components/admin/AdminLayout';
import { userService, User, UserRole, UserCreate, UserUpdate } from '../../../services/admin';
import { useAuth } from '../../../hooks/useAuth';

const AdminUsers: React.FC = () => {
  const { user: currentUser } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [roleFilter, setRoleFilter] = useState<string>('');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalCount, setTotalCount] = useState(0);

  // Search states
  const [searchQuery, setSearchQuery] = useState('');
  const [tempSearchQuery, setTempSearchQuery] = useState('');

  // Dialog states
  const [openDialog, setOpenDialog] = useState(false);
  const [dialogMode, setDialogMode] = useState<'create' | 'edit'>('create');
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [userToDelete, setUserToDelete] = useState<User | null>(null);

  // Form data
  const [formData, setFormData] = useState<UserCreate & { id?: number }>({
    username: '',
    email: '',
    full_name: '',
    password: '',
    role: UserRole.CUSTOMER,
  });

  const isCurrentUser = (user: User) => {
    return currentUser ? user.id === currentUser.id : false;
  };

  // Helper function to extract error message safely
  const getErrorMessage = (err: any): string => {
    // If it's a simple string message
    if (typeof err === 'string') {
      return err;
    }
    
    // If it's an error response with detail
    if (err.response?.data?.detail) {
      const detail = err.response.data.detail;
      
      // If detail is an array of validation errors (from Pydantic)
      if (Array.isArray(detail)) {
        return detail.map((d: any) => 
          typeof d === 'string' ? d : d.msg || JSON.stringify(d)
        ).join('; ');
      }
      
      // If detail is a string
      if (typeof detail === 'string') {
        return detail;
      }
    }
    
    // Default error message
    return 'Có lỗi xảy ra. Vui lòng thử lại.';
  };

  // Validation helper functions
  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const validateForm = (): string | null => {
    // Validate email
    if (!formData.email.trim()) {
      return 'Email là bắt buộc';
    }
    if (!validateEmail(formData.email)) {
      return 'Email không hợp lệ';
    }

    // Validate username
    if (!formData.username.trim()) {
      return 'Tên đăng nhập là bắt buộc';
    }

    // Validate full name
    if (!formData.full_name.trim()) {
      return 'Họ tên là bắt buộc';
    }

    // Validate password for create mode
    if (dialogMode === 'create') {
      if (!formData.password) {
        return 'Mật khẩu là bắt buộc';
      }
      if (formData.password.length < 6) {
        return 'Mật khẩu phải có ít nhất 6 ký tự';
      }
    }

    // Validate password for edit mode (if provided)
    if (dialogMode === 'edit' && formData.password.trim()) {
      if (formData.password.length < 6) {
        return 'Mật khẩu phải có ít nhất 6 ký tự';
      }
    }

    return null;
  };

  useEffect(() => {
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [roleFilter, page, rowsPerPage, searchQuery]);

  const loadData = async () => {
    try {
      setLoading(true);
      const skip = page * rowsPerPage;
      const response = await userService.getUsers(skip, rowsPerPage);
      const usersData = response;
      
      // Filter by role and search query
      let filteredUsers = roleFilter 
        ? usersData.filter((user: User) => user.role === roleFilter)
        : usersData;
        
      if (searchQuery) {
        filteredUsers = filteredUsers.filter(user => 
          user.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
          user.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
          user.full_name.toLowerCase().includes(searchQuery.toLowerCase())
        );
      }
      
      setUsers(filteredUsers);
      setTotalCount(filteredUsers.length);
      setError(null);
    } catch (err: any) {
      setError(getErrorMessage(err));
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
    setRoleFilter('');
    setPage(0);
  };

  const handleCreateUser = () => {
    setDialogMode('create');
    setFormData({
      username: '',
      email: '',
      full_name: '',
      password: '',
      role: UserRole.CUSTOMER,
    });
    setOpenDialog(true);
  };

  const handleEditUser = (user: User) => {
    setDialogMode('edit');
    setSelectedUser(user);
    setFormData({
      id: user.id,
      username: user.username,
      email: user.email,
      full_name: user.full_name,
      password: '',
      role: user.role,
    });
    setOpenDialog(true);
  };

  const handleDeleteUser = (user: User) => {
    setUserToDelete(user);
    setDeleteConfirmOpen(true);
  };

  const confirmDelete = async () => {
    if (!userToDelete) return;
    
    try {
      setLoading(true);
      await userService.deleteUser(userToDelete.id);
      setSuccess('Xóa người dùng thành công');
      setDeleteConfirmOpen(false);
      setUserToDelete(null);
      await loadData();
    } catch (err: any) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    // Validate form before submitting
    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    try {
      setLoading(true);
      
      if (dialogMode === 'create') {
        await userService.createUser(formData);
        setSuccess('Thêm người dùng thành công');
      } else if (dialogMode === 'edit' && formData.id) {
        const updateData: UserUpdate = {
          username: formData.username,
          email: formData.email,
          full_name: formData.full_name,
          role: formData.role,
        };
        
        // Chỉ cập nhật password nếu có nhập
        if (formData.password.trim()) {
          updateData.password = formData.password;
        }
        
        await userService.updateUser(formData.id, updateData);
        setSuccess('Cập nhật người dùng thành công');
      }
      
      setOpenDialog(false);
      await loadData();
    } catch (err: any) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const getRoleColor = (role: UserRole) => {
    switch (role) {
      case UserRole.ADMIN:
        return 'error';
      case UserRole.MANAGER:
        return 'warning';
      case UserRole.STAFF:
        return 'info';
      default:
        return 'default';
    }
  };

  const getRoleLabel = (role: UserRole) => {
    switch (role) {
      case UserRole.ADMIN:
        return 'Quản trị viên';
      case UserRole.MANAGER:
        return 'Quản lý';
      case UserRole.STAFF:
        return 'Nhân viên';
      case UserRole.CUSTOMER:
        return 'Khách hàng';
      default:
        return role;
    }
  };

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  if (loading && users.length === 0) {
    return (
      <AdminLayout>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
          <CircularProgress />
        </Box>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout>
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
            Quản lý người dùng
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleCreateUser}
     
          >
            Thêm người dùng
          </Button>
        </Box>

        {/* Search and Filter Section */}
        <Card sx={{ mb: 3, p: 2 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                placeholder="Tìm kiếm theo tên, email..."
                value={tempSearchQuery}
                onChange={(e) => setTempSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                InputProps={{
                  endAdornment: (
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <IconButton onClick={handleSearch} size="small">
                        <SearchIcon />
                      </IconButton>
                      {(searchQuery || roleFilter) && (
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
                <InputLabel>Lọc theo vai trò</InputLabel>
                <Select
                  value={roleFilter}
                  label="Lọc theo vai trò"
                  onChange={(e) => setRoleFilter(e.target.value)}
                >
                  <MuiMenuItem value="">Tất cả</MuiMenuItem>
                  <MuiMenuItem value={UserRole.ADMIN}>Quản trị viên</MuiMenuItem>
                  <MuiMenuItem value={UserRole.MANAGER}>Quản lý</MuiMenuItem>
                  <MuiMenuItem value={UserRole.STAFF}>Nhân viên</MuiMenuItem>
                  <MuiMenuItem value={UserRole.CUSTOMER}>Khách hàng</MuiMenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={5}>
              <Typography variant="body2" color="textSecondary">
                {searchQuery && `Tìm kiếm: "${searchQuery}" | `}
                {roleFilter && `Vai trò: ${getRoleLabel(roleFilter as UserRole)} | `}
                Tổng cộng: {totalCount} người dùng
              </Typography>
            </Grid>
          </Grid>
        </Card>

        <Card>
          <TableContainer component={Paper}>
              <Table>
                <TableHead sx={{ bgcolor: '#f5f5f5' }}>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 'bold' }}>Tên đăng nhập</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>Email</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>Họ tên</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }} align="center">Vai trò</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }} align="center">Trạng thái</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>Ngày tạo</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }} align="center">Hành động</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {users && users.length > 0 ? users.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage).map((user) => (
                    <TableRow key={user.id} hover>
                      <TableCell>{user.username}</TableCell>
                      <TableCell>{user.email}</TableCell>
                      <TableCell>{user.full_name}</TableCell>
                      <TableCell align="center">
                        <Chip
                          label={getRoleLabel(user.role)}
                          color={getRoleColor(user.role)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell align="center">
                        <Chip
                          label={user.is_active ? 'Hoạt động' : 'Không hoạt động'}
                          color={user.is_active ? 'success' : 'error'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        {new Date(user.created_at).toLocaleDateString('vi-VN')}
                      </TableCell>
                      <TableCell align="center">
            
                        <Button 
                          size="small" 
                          startIcon={<EditIcon />} 
                          color="info" 
                          onClick={() => handleEditUser(user)} 
                          disabled={isCurrentUser(user)}
                          sx={{ mr: 1 }}
                        >
                          Sửa
                        </Button>
                        <Button 
                          size="small" 
                          startIcon={<DeleteIcon />} 
                          color="error" 
                          onClick={() => handleDeleteUser(user)}
                          disabled={isCurrentUser(user)}
                        >
                          Xóa
                        </Button>
                      </TableCell>
                    </TableRow>
                  )) : (
                    <TableRow>
                      <TableCell colSpan={8} align="center" sx={{ py: 3 }}>
                        <Typography color="textSecondary">
                          {loading ? 'Đang tải...' : 'Không có người dùng nào'}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
            <TablePagination
              component="div"
              count={totalCount}
              rowsPerPage={rowsPerPage}
              page={page}
              onPageChange={handleChangePage}
              onRowsPerPageChange={handleChangeRowsPerPage}
              labelRowsPerPage="Số hàng mỗi trang:"
              labelDisplayedRows={({ from, to, count }) =>
                `${from}-${to} trong tổng số ${count !== -1 ? count : `hơn ${to}`}`
              }
            />
          </Card>

        {/* User Dialog */}
        <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
          <DialogTitle>
            {dialogMode === 'create' ? 'Thêm người dùng mới' : 'Chỉnh sửa người dùng'}
          </DialogTitle>
          <DialogContent>
            <Box sx={{ pt: 1 }}>
              {dialogMode === 'edit' && selectedUser && isCurrentUser(selectedUser) && (
                <Alert severity="info" sx={{ mb: 2 }}>
                  Bạn đang chỉnh sửa tài khoản của chính mình. Hãy cẩn thận khi thay đổi thông tin.
                </Alert>
              )}
              <Box>
                <TextField
                  fullWidth
                  label="Tên đăng nhập"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  margin="normal"
                  required
                />
                <TextField
                  fullWidth
                  label="Email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  margin="normal"
                  required
                />
                <TextField
                  fullWidth
                  label="Họ tên"
                  value={formData.full_name}
                  onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                  margin="normal"
                  required
                />
                <TextField
                  fullWidth
                  label={dialogMode === 'create' ? "Mật khẩu" : "Mật khẩu mới (để trống nếu không đổi)"}
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  margin="normal"
                  required={dialogMode === 'create'}
                  helperText={dialogMode === 'edit' ? "Chỉ nhập nếu muốn thay đổi mật khẩu" : ""}
                />
                <FormControl fullWidth margin="normal">
                  <InputLabel>Vai trò</InputLabel>
                  <Select
                    value={formData.role}
                    onChange={(e) => setFormData({ ...formData, role: e.target.value as UserRole })}
                    label="Vai trò"
                  >
                    <MuiMenuItem value={UserRole.CUSTOMER}>Khách hàng</MuiMenuItem>
                    <MuiMenuItem value={UserRole.STAFF}>Nhân viên</MuiMenuItem>
                    <MuiMenuItem value={UserRole.MANAGER}>Quản lý</MuiMenuItem>
                    <MuiMenuItem value={UserRole.ADMIN}>Quản trị viên</MuiMenuItem>
                  </Select>
                </FormControl>
              </Box>
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpenDialog(false)}>Hủy</Button>
            <Button onClick={handleSubmit} variant="contained">
              {dialogMode === 'create' ? 'Thêm' : 'Cập nhật'}
            </Button>
          </DialogActions>
        </Dialog>

        {/* Delete Confirmation Dialog */}
        <Dialog open={deleteConfirmOpen} onClose={() => setDeleteConfirmOpen(false)}>
          <DialogTitle>Xác nhận xóa</DialogTitle>
          <DialogContent>
            <Typography>
              Bạn có chắc chắn muốn xóa người dùng "{userToDelete?.full_name}" không?
              Hành động này không thể hoàn tác.
            </Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDeleteConfirmOpen(false)}>Hủy</Button>
            <Button onClick={confirmDelete} color="error" variant="contained">
              Xóa
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

export default AdminUsers;