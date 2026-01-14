import React, { useState } from 'react';
import {
  Box,
  AppBar,
  Toolbar,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Typography,
  Avatar,
  Menu,
  MenuItem,
  Divider,
  Container,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  RestaurantMenu as MenuIcon,
  Category as CategoryIcon,
  TableBar as TablesIcon,
  ShoppingCart as OrdersIcon,
  EventAvailable as ReservationsIcon,
  People as UsersIcon,
  Logout as LogoutIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

const DRAWER_WIDTH = 250;

interface AdminLayoutProps {
  children: React.ReactNode;
}

const AdminLayout: React.FC<AdminLayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const menuItems = [
    {
      label: 'Bảng điều khiển',
      icon: <DashboardIcon />,
      path: '/admin/dashboard',
    },
    {
      label: 'Quản lý thực đơn',
      icon: <MenuIcon />,
      path: '/admin/menu',
    },
    {
      label: 'Quản lý danh mục',
      icon: <CategoryIcon />,
      path: '/admin/categories',
    },
    {
      label: 'Quản lý bàn',
      icon: <TablesIcon />,
      path: '/admin/tables',
    },
    {
      label: 'Quản lý đơn hàng',
      icon: <OrdersIcon />,
      path: '/admin/orders',
    },
    {
      label: 'Quản lý đặt bàn',
      icon: <ReservationsIcon />,
      path: '/admin/reservations',
    },
    {
      label: 'Quản lý người dùng',
      icon: <UsersIcon />,
      path: '/admin/users',
    },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: '#f5f5f5' }}>
      {/* Drawer/Sidebar - Luôn hiển thị */}
      <Drawer
        variant="permanent"
        sx={{
          width: DRAWER_WIDTH,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: DRAWER_WIDTH,
            boxSizing: 'border-box',
            bgcolor: '#2c3e50',
            color: '#ffffff',
            borderRight: '1px solid rgba(0,0,0,0.12)',
            display: 'flex',
            flexDirection: 'column',
          },
        }}
      >
        {/* Logo/Header */}
        <Box sx={{ p: 2, bgcolor: '#1a252f', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
          <Typography variant="h6" sx={{ fontWeight: 'bold', textAlign: 'center' }}>
            🍽️ RestoBot
          </Typography>
        </Box>

        {/* Menu */}
        <List sx={{ p: 0, flex: 1 }}>
          {menuItems.map((item) => (
            <ListItem
              button
              key={item.path}
              onClick={() => navigate(item.path)}
              sx={{
                bgcolor: isActive(item.path) ? 'rgba(25, 118, 210, 0.2)' : 'transparent',
                borderLeft: isActive(item.path) ? '4px solid #1976d2' : '4px solid transparent',
                transition: 'all 0.3s',
                '&:hover': {
                  bgcolor: 'rgba(25, 118, 210, 0.15)',
                },
              }}
            >
              <ListItemIcon
                sx={{
                  color: isActive(item.path) ? '#1976d2' : '#ffffff',
                  minWidth: 40,
                }}
              >
                {item.icon}
              </ListItemIcon>
              <ListItemText
                primary={item.label}
                primaryTypographyProps={{
                  sx: {
                    fontWeight: isActive(item.path) ? 'bold' : 'normal',
                    fontSize: '0.95rem',
                  },
                }}
              />
            </ListItem>
          ))}
        </List>

        {/* Logout Button */}
        <Box sx={{ p: 2, borderTop: '1px solid rgba(255,255,255,0.1)' }}>
          <ListItem
            button
            onClick={handleLogout}
            sx={{
              bgcolor: 'rgba(211, 47, 47, 0.1)',
              borderRadius: 1,
              transition: 'all 0.3s',
              '&:hover': {
                bgcolor: 'rgba(211, 47, 47, 0.2)',
              },
            }}
          >
            <ListItemIcon sx={{ color: '#d32f2f', minWidth: 40 }}>
              <LogoutIcon />
            </ListItemIcon>
            <ListItemText
              primary="Đăng xuất"
              primaryTypographyProps={{ sx: { fontSize: '0.95rem' } }}
            />
          </ListItem>
        </Box>
      </Drawer>

      {/* Main Content Area */}
      <Box
        sx={{
          flexGrow: 1,
          display: 'flex',
          flexDirection: 'column',
          width: `calc(100% - ${DRAWER_WIDTH}px)`,
        }}
      >
        {/* AppBar */}
        <AppBar
          position="sticky"
          sx={{
            bgcolor: '#ffffff',
            color: '#333',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          }}
        >
          <Toolbar>
            <Typography variant="h6" sx={{ flexGrow: 1, fontWeight: 'bold', color: '#fff' }}>
           
            </Typography>

            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Avatar
                onClick={handleProfileMenuOpen}
                sx={{
              
                  cursor: 'pointer',
                  transition: 'transform 0.2s',
                  '&:hover': { transform: 'scale(1.1)' },
                }}
              >
                {user?.username?.charAt(0).toUpperCase() || 'A'}
              </Avatar>
            </Box>

            {/* Profile Menu */}
            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleProfileMenuClose}
              anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
              transformOrigin={{ vertical: 'top', horizontal: 'right' }}
            >
              <MenuItem disabled>
                <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                  {user?.username || 'User'}
                </Typography>
              </MenuItem>
              <Divider />
              <MenuItem onClick={() => navigate('/admin/profile')}>
                <Typography variant="body2">Hồ sơ của tôi</Typography>
              </MenuItem>
            </Menu>
          </Toolbar>
        </AppBar>

        {/* Main Content */}
        <Box
          component="main"
          sx={{
            flex: 1,
            overflow: 'auto',
            p: 3,
          }}
        >
          <Container maxWidth="lg">
            {children}
          </Container>
        </Box>
      </Box>
    </Box>
  );
};

export default AdminLayout;
