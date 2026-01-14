import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Avatar,
  Grid,
  TextField,
  Button,
  Alert,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  OutlinedInput,
  InputAdornment,
  IconButton,
} from '@mui/material';
import {
  Person as PersonIcon,
  Edit as EditIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  VpnKey as VpnKeyIcon,
  Visibility,
  VisibilityOff,
} from '@mui/icons-material';
import AdminLayout from '../../../components/admin/AdminLayout';
import { useAuth } from '../../../hooks/useAuth';
import { userService } from '../../../services/userService';
import { UpdateProfileRequest, ChangePasswordRequest } from '../../../types';

const AdminProfile: React.FC = () => {
  const { user, updateUser } = useAuth();
  const [editMode, setEditMode] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [changePasswordOpen, setChangePasswordOpen] = useState(false);
  
  // Profile form state
  const [profileForm, setProfileForm] = useState({
    email: user?.email || '',
    username: user?.username || '',
    full_name: user?.full_name || '',
    phone: user?.phone || '',
  });

  // Password form state
  const [passwordForm, setPasswordForm] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });

  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false,
  });

  const [passwordErrors, setPasswordErrors] = useState<string[]>([]);

  useEffect(() => {
    if (user) {
      setProfileForm({
        email: user.email,
        username: user.username,
        full_name: user.full_name,
        phone: user.phone || '',
      });
    }
  }, [user]);

  const handleProfileChange = (field: keyof typeof profileForm) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setProfileForm(prev => ({
      ...prev,
      [field]: event.target.value,
    }));
  };

  const handlePasswordChange = (field: keyof typeof passwordForm) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setPasswordForm(prev => ({
      ...prev,
      [field]: event.target.value,
    }));
  };

  const togglePasswordVisibility = (field: keyof typeof showPasswords) => {
    setShowPasswords(prev => ({
      ...prev,
      [field]: !prev[field],
    }));
  };

  const validatePasswordForm = (): boolean => {
    const errors: string[] = [];

    if (!passwordForm.currentPassword) {
      errors.push('Vui lòng nhập mật khẩu hiện tại');
    }

    if (!passwordForm.newPassword) {
      errors.push('Vui lòng nhập mật khẩu mới');
    } else if (passwordForm.newPassword.length < 6) {
      errors.push('Mật khẩu mới phải có ít nhất 6 ký tự');
    }

    if (!passwordForm.confirmPassword) {
      errors.push('Vui lòng xác nhận mật khẩu mới');
    } else if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      errors.push('Xác nhận mật khẩu không khớp');
    }

    if (passwordForm.currentPassword === passwordForm.newPassword) {
      errors.push('Mật khẩu mới phải khác mật khẩu hiện tại');
    }

    setPasswordErrors(errors);
    return errors.length === 0;
  };

  const handleUpdateProfile = async () => {
    if (!user) return;
    
    setLoading(true);
    setMessage(null);

    try {
      const updateData: UpdateProfileRequest = {
        email: profileForm.email,
        username: profileForm.username,
        full_name: profileForm.full_name,
        phone: profileForm.phone || undefined,
      };

      const updatedUser = await userService.updateProfile(updateData);
      updateUser(updatedUser);
      setEditMode(false);
      setMessage({ type: 'success', text: 'Cập nhật thông tin thành công!' });
    } catch (error: any) {
      setMessage({ 
        type: 'error', 
        text: error.message || 'Có lỗi xảy ra khi cập nhật thông tin' 
      });
    } finally {
      setLoading(false);
    }
  };

  const handleChangePassword = async () => {
    if (!validatePasswordForm()) {
      return;
    }

    setLoading(true);

    try {
      const changePasswordData: ChangePasswordRequest = {
        current_password: passwordForm.currentPassword,
        new_password: passwordForm.newPassword,
      };

      await userService.changePassword(changePasswordData);
      setChangePasswordOpen(false);
      setPasswordForm({
        currentPassword: '',
        newPassword: '',
        confirmPassword: '',
      });
      setPasswordErrors([]);
      setMessage({ type: 'success', text: 'Đổi mật khẩu thành công!' });
    } catch (error: any) {
      setPasswordErrors([error.message || 'Có lỗi xảy ra khi đổi mật khẩu']);
    } finally {
      setLoading(false);
    }
  };

  const handleCancelEdit = () => {
    if (user) {
      setProfileForm({
        email: user.email,
        username: user.username,
        full_name: user.full_name,
        phone: user.phone || '',
      });
    }
    setEditMode(false);
    setMessage(null);
  };

  const handleClosePasswordDialog = () => {
    setChangePasswordOpen(false);
    setPasswordForm({
      currentPassword: '',
      newPassword: '',
      confirmPassword: '',
    });
    setPasswordErrors([]);
    setShowPasswords({
      current: false,
      new: false,
      confirm: false,
    });
  };

  if (!user) {
    return (
      <AdminLayout>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <Typography>Đang tải...</Typography>
        </Box>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout>
      <Box sx={{ maxWidth: 800, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom>
        Hồ sơ cá nhân
      </Typography>

      {message && (
        <Alert 
          severity={message.type} 
          sx={{ mb: 3 }}
          onClose={() => setMessage(null)}
        >
          {message.text}
        </Alert>
      )}

      <Card>
        <CardContent>
          <Box display="flex" alignItems="center" mb={3}>
            <Avatar
              sx={{ 
                width: 80, 
                height: 80, 
                mr: 3,
                bgcolor: 'primary.main',
                fontSize: '2rem'
              }}
            >
              <PersonIcon fontSize="large" />
            </Avatar>
            <Box>
              <Typography variant="h5" gutterBottom>
                {user.full_name}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                @{user.username} • {user.role}
              </Typography>
            </Box>
          </Box>

          <Divider sx={{ my: 3 }} />

          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Email"
                value={profileForm.email}
                onChange={handleProfileChange('email')}
                disabled={!editMode}
                variant="outlined"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Tên đăng nhập"
                value={profileForm.username}
                onChange={handleProfileChange('username')}
                disabled={!editMode}
                variant="outlined"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Họ và tên"
                value={profileForm.full_name}
                onChange={handleProfileChange('full_name')}
                disabled={!editMode}
                variant="outlined"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Số điện thoại"
                value={profileForm.phone}
                onChange={handleProfileChange('phone')}
                disabled={!editMode}
                variant="outlined"
              />
            </Grid>
            <Grid item xs={12}>
              <Typography variant="body2" color="text.secondary">
                Ngày tạo: {new Date(user.created_at).toLocaleDateString('vi-VN')}
                {user.updated_at && (
                  <> • Cập nhật lần cuối: {new Date(user.updated_at).toLocaleDateString('vi-VN')}</>
                )}
              </Typography>
            </Grid>
          </Grid>

          <Box display="flex" gap={2} mt={4}>
            {!editMode ? (
              <>
                <Button
                  variant="contained"
                  startIcon={<EditIcon />}
                  onClick={() => setEditMode(true)}
                >
                  Chỉnh sửa thông tin
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<VpnKeyIcon />}
                  onClick={() => setChangePasswordOpen(true)}
                >
                  Đổi mật khẩu
                </Button>
              </>
            ) : (
              <>
                <Button
                  variant="contained"
                  startIcon={<SaveIcon />}
                  onClick={handleUpdateProfile}
                  disabled={loading}
                >
                  Lưu thay đổi
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<CancelIcon />}
                  onClick={handleCancelEdit}
                  disabled={loading}
                >
                  Hủy
                </Button>
              </>
            )}
          </Box>
        </CardContent>
      </Card>

      {/* Change Password Dialog */}
      <Dialog
        open={changePasswordOpen}
        onClose={handleClosePasswordDialog}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Đổi mật khẩu</DialogTitle>
        <DialogContent>
          {passwordErrors.length > 0 && (
            <Alert severity="error" sx={{ mb: 2 }}>
              <ul style={{ margin: 0, paddingLeft: 20 }}>
                {passwordErrors.map((error, index) => (
                  <li key={index}>{error}</li>
                ))}
              </ul>
            </Alert>
          )}

          <FormControl fullWidth margin="normal" variant="outlined">
            <InputLabel>Mật khẩu hiện tại</InputLabel>
            <OutlinedInput
              type={showPasswords.current ? 'text' : 'password'}
              value={passwordForm.currentPassword}
              onChange={handlePasswordChange('currentPassword')}
              endAdornment={
                <InputAdornment position="end">
                  <IconButton
                    onClick={() => togglePasswordVisibility('current')}
                    edge="end"
                  >
                    {showPasswords.current ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              }
              label="Mật khẩu hiện tại"
            />
          </FormControl>

          <FormControl fullWidth margin="normal" variant="outlined">
            <InputLabel>Mật khẩu mới</InputLabel>
            <OutlinedInput
              type={showPasswords.new ? 'text' : 'password'}
              value={passwordForm.newPassword}
              onChange={handlePasswordChange('newPassword')}
              endAdornment={
                <InputAdornment position="end">
                  <IconButton
                    onClick={() => togglePasswordVisibility('new')}
                    edge="end"
                  >
                    {showPasswords.new ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              }
              label="Mật khẩu mới"
            />
          </FormControl>

          <FormControl fullWidth margin="normal" variant="outlined">
            <InputLabel>Xác nhận mật khẩu mới</InputLabel>
            <OutlinedInput
              type={showPasswords.confirm ? 'text' : 'password'}
              value={passwordForm.confirmPassword}
              onChange={handlePasswordChange('confirmPassword')}
              endAdornment={
                <InputAdornment position="end">
                  <IconButton
                    onClick={() => togglePasswordVisibility('confirm')}
                    edge="end"
                  >
                    {showPasswords.confirm ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              }
              label="Xác nhận mật khẩu mới"
            />
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={handleClosePasswordDialog}
            disabled={loading}
          >
            Hủy
          </Button>
          <Button 
            variant="contained"
            onClick={handleChangePassword}
            disabled={loading}
          >
            Đổi mật khẩu
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
    </AdminLayout>
  );
};

export default AdminProfile;