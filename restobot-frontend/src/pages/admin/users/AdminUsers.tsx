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
  TextField,

  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
} from '@mui/icons-material';
import AdminLayout from '../../../components/admin/AdminLayout';
import { userService, User, UserRole, UserCreate, UserUpdate } from '../../../services/adminService';

const AdminUsers: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [roleFilter, setRoleFilter] = useState<string>('');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalCount, setTotalCount] = useState(0);

  // Dialog states
  const [openDialog, setOpenDialog] = useState(false);
  const [dialogMode, setDialogMode] = useState<'view' | 'create' | 'edit'>('view');
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

  useEffect(() => {
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [roleFilter, page, rowsPerPage]);

  const loadData = async () => {
    try {
      setLoading(true);
      const skip = page * rowsPerPage;
      const response = await userService.getUsers(skip, rowsPerPage);
      const usersData = response;
      
      // Filter by role if specified
      const filteredUsers = roleFilter 
        ? usersData.filter((user: User) => user.role === roleFilter)
        : usersData;
      
      setUsers(filteredUsers);
      setTotalCount(filteredUsers.length);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Lỗi tải dữ liệu người dùng');
    } finally {
      setLoading(false);
    }
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

  const handleViewUser = (user: User) => {
    setDialogMode('view');
    setSelectedUser(user);
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
      setDeleteConfirmOpen(false);
      setUserToDelete(null);
      await loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Lỗi xóa người dùng');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    try {
      setLoading(true);
      
      if (dialogMode === 'create') {
        await userService.createUser(formData);
      } else if (dialogMode === 'edit' && formData.id) {
        const updateData: UserUpdate = {
          username: formData.username,
          email: formData.email,
          full_name: formData.full_name,
          role: formData.role,
        };
        await userService.updateUser(formData.id, updateData);
      }
      
      setOpenDialog(false);
      await loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Lỗi lưu dữ liệu người dùng');
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
      <Box p={3}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h4" component="h1">
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

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Card>
          <Box p={2}>
            <Box display="flex" gap={2} mb={2}>
              <FormControl size="small" sx={{ minWidth: 200 }}>
                <InputLabel>Lọc theo vai trò</InputLabel>
                <Select
                  value={roleFilter}
                  onChange={(e) => setRoleFilter(e.target.value)}
                  label="Lọc theo vai trò"
                >
                  <MuiMenuItem value="">Tất cả</MuiMenuItem>
                  <MuiMenuItem value={UserRole.ADMIN}>Quản trị viên</MuiMenuItem>
                  <MuiMenuItem value={UserRole.MANAGER}>Quản lý</MuiMenuItem>
                  <MuiMenuItem value={UserRole.STAFF}>Nhân viên</MuiMenuItem>
                  <MuiMenuItem value={UserRole.CUSTOMER}>Khách hàng</MuiMenuItem>
                </Select>
              </FormControl>
            </Box>

            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>ID</TableCell>
                    <TableCell>Tên đăng nhập</TableCell>
                    <TableCell>Email</TableCell>
                    <TableCell>Họ tên</TableCell>
                    <TableCell>Vai trò</TableCell>
                    <TableCell>Trạng thái</TableCell>
                    <TableCell>Ngày tạo</TableCell>
                    <TableCell align="center">Thao tác</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {users.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage).map((user) => (
                    <TableRow key={user.id} hover>
                      <TableCell>{user.id}</TableCell>
                      <TableCell>{user.username}</TableCell>
                      <TableCell>{user.email}</TableCell>
                      <TableCell>{user.full_name}</TableCell>
                      <TableCell>
                        <Chip
                          label={getRoleLabel(user.role)}
                          color={getRoleColor(user.role)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
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
                        <Tooltip title="Xem chi tiết">
                          <IconButton onClick={() => handleViewUser(user)} size="small">
                            <ViewIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Chỉnh sửa">
                          <IconButton onClick={() => handleEditUser(user)} size="small">
                            <EditIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Xóa">
                          <IconButton 
                            onClick={() => handleDeleteUser(user)} 
                            size="small"
                            color="error"
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
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
          </Box>
        </Card>

        {/* User Dialog */}
        <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
          <DialogTitle>
            {dialogMode === 'create' && 'Thêm người dùng mới'}
            {dialogMode === 'edit' && 'Chỉnh sửa người dùng'}
            {dialogMode === 'view' && 'Chi tiết người dùng'}
          </DialogTitle>
          <DialogContent>
            <Box sx={{ pt: 1 }}>
              {dialogMode === 'view' && selectedUser ? (
                <Box>
                  <Typography><strong>ID:</strong> {selectedUser.id}</Typography>
                  <Typography><strong>Tên đăng nhập:</strong> {selectedUser.username}</Typography>
                  <Typography><strong>Email:</strong> {selectedUser.email}</Typography>
                  <Typography><strong>Họ tên:</strong> {selectedUser.full_name}</Typography>
                  <Typography><strong>Vai trò:</strong> {getRoleLabel(selectedUser.role)}</Typography>
                  <Typography><strong>Trạng thái:</strong> {selectedUser.is_active ? 'Hoạt động' : 'Không hoạt động'}</Typography>
                  <Typography><strong>Ngày tạo:</strong> {new Date(selectedUser.created_at).toLocaleString('vi-VN')}</Typography>
                </Box>
              ) : (
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
                  {dialogMode === 'create' && (
                    <TextField
                      fullWidth
                      label="Mật khẩu"
                      type="password"
                      value={formData.password}
                      onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                      margin="normal"
                      required
                    />
                  )}
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
              )}
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpenDialog(false)}>
              {dialogMode === 'view' ? 'Đóng' : 'Hủy'}
            </Button>
            {dialogMode !== 'view' && (
              <Button onClick={handleSubmit} variant="contained">
                {dialogMode === 'create' ? 'Thêm' : 'Cập nhật'}
              </Button>
            )}
          </DialogActions>
        </Dialog>

        {/* Delete Confirmation Dialog */}
        <Dialog open={deleteConfirmOpen} onClose={() => setDeleteConfirmOpen(false)}>
          <DialogTitle>Xác nhận xóa</DialogTitle>
          <DialogContent>
            <Typography>
              Bạn có chắc chắn muốn xóa người dùng "{userToDelete?.full_name}" không?
            </Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDeleteConfirmOpen(false)}>Hủy</Button>
            <Button onClick={confirmDelete} color="error" variant="contained">
              Xóa
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </AdminLayout>
  );
};

export default AdminUsers;