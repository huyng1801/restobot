import { createBrowserRouter, Navigate } from 'react-router-dom';
import { lazy, Suspense } from 'react';
import Layout from '../components/layout/Layout';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ProtectedRoute from '../components/auth/ProtectedRoute';
import AdminRoute from '../components/auth/AdminRoute';

// Lazy load components for better performance
const Login = lazy(() => import('../pages/auth/Login'));
const Register = lazy(() => import('../pages/auth/Register'));
const Chat = lazy(() => import('../pages/customer/Chat'));
// Admin pages
const Dashboard = lazy(() => import('../pages/admin/Dashboard'));
const AdminMenu = lazy(() => import('../pages/admin/menu/AdminMenu'));
const AdminCategories = lazy(() => import('../pages/admin/categories/AdminCategories'));
const AdminTables = lazy(() => import('../pages/admin/tables/AdminTables'));
const AdminOrders = lazy(() => import('../pages/admin/orders/AdminOrders'));
const AdminReservations = lazy(() => import('../pages/admin/reservations/AdminReservations'));
const AdminUsers = lazy(() => import('../pages/admin/users/AdminUsers'));
const AdminProfile = lazy(() => import('../pages/admin/profile/AdminProfile'));

// Error pages
const NotFound = lazy(() => import('../pages/error/NotFound'));
const Unauthorized = lazy(() => import('../pages/error/Unauthorized'));

// Wrapper component for lazy loading with suspense
const SuspenseWrapper = ({ children }: { children: React.ReactNode }) => (
  <Suspense fallback={<LoadingSpinner />}>
    {children}
  </Suspense>
);

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      // Public routes
      {
        path: '',
        element: <Navigate to="/chat" replace />,
      },
      {
        path: 'login',
        element: (
          <SuspenseWrapper>
            <Login />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'register',
        element: (
          <SuspenseWrapper>
            <Register />
          </SuspenseWrapper>
        ),
      },
      
      // Protected customer routes
      {
        path: 'chat',
        element: (
          <ProtectedRoute>
            <SuspenseWrapper>
              <Chat />
            </SuspenseWrapper>
          </ProtectedRoute>
        ),
      },
      
      // Admin routes
      {
        path: 'admin',
        element: (
          <AdminRoute>
            <Navigate to="/admin/dashboard" replace />
          </AdminRoute>
        ),
      },
      {
        path: 'admin/dashboard',
        element: (
          <AdminRoute>
            <SuspenseWrapper>
              <Dashboard />
            </SuspenseWrapper>
          </AdminRoute>
        ),
      },
      {
        path: 'admin/menu',
        element: (
          <AdminRoute>
            <SuspenseWrapper>
              <AdminMenu />
            </SuspenseWrapper>
          </AdminRoute>
        ),
      },
      {
        path: 'admin/categories',
        element: (
          <AdminRoute>
            <SuspenseWrapper>
              <AdminCategories />
            </SuspenseWrapper>
          </AdminRoute>
        ),
      },
      {
        path: 'admin/tables',
        element: (
          <AdminRoute>
            <SuspenseWrapper>
              <AdminTables />
            </SuspenseWrapper>
          </AdminRoute>
        ),
      },
      {
        path: 'admin/orders',
        element: (
          <AdminRoute>
            <SuspenseWrapper>
              <AdminOrders />
            </SuspenseWrapper>
          </AdminRoute>
        ),
      },
      {
        path: 'admin/reservations',
        element: (
          <AdminRoute>
            <SuspenseWrapper>
              <AdminReservations />
            </SuspenseWrapper>
          </AdminRoute>
        ),
      },
      {
        path: 'admin/users',
        element: (
          <AdminRoute>
            <SuspenseWrapper>
              <AdminUsers />
            </SuspenseWrapper>
          </AdminRoute>
        ),
      },
      {
        path: 'admin/profile',
        element: (
          <AdminRoute>
            <SuspenseWrapper>
              <AdminProfile />
            </SuspenseWrapper>
          </AdminRoute>
        ),
      },

      
      // Error routes
      {
        path: 'unauthorized',
        element: (
          <SuspenseWrapper>
            <Unauthorized />
          </SuspenseWrapper>
        ),
      },
      {
        path: '*',
        element: (
          <SuspenseWrapper>
            <NotFound />
          </SuspenseWrapper>
        ),
      },
    ],
  },
]);

/**
 * Navigation helper functions
 */

export const routes = {
  // Public routes
  home: '/',
  login: '/login',
  register: '/register',
  
  // Customer routes
  chat: '/chat',
  menu: '/menu',
  orders: '/orders',
  reservations: '/reservations',
  profile: '/profile',
  
  // Admin routes
  admin: '/admin',
  adminDashboard: '/admin/dashboard',
  adminMenu: '/admin/menu',
  adminTables: '/admin/tables',
  adminOrders: '/admin/orders',
  adminReservations: '/admin/reservations',
  adminUsers: '/admin/users',
  adminProfile: '/admin/profile',
  
  // Error routes
  unauthorized: '/unauthorized',
  notFound: '/404',
};

export const getRouteTitle = (pathname: string): string => {
  const routeTitles: Record<string, string> = {
    [routes.home]: 'Trang chủ',
    [routes.login]: 'Đăng nhập',
    [routes.register]: 'Đăng ký',
    [routes.chat]: 'Trò chuyện',
    [routes.menu]: 'Thực đơn',
    [routes.orders]: 'Đơn hàng của tôi',
    [routes.reservations]: 'Đặt bàn của tôi',
    [routes.profile]: 'Hồ sơ',
    [routes.admin]: 'Quản trị',
    [routes.adminDashboard]: 'Bảng điều khiển',
    [routes.adminMenu]: 'Quản lý thực đơn',
    [routes.adminTables]: 'Quản lý bàn',
    [routes.adminOrders]: 'Quản lý đơn hàng',
    [routes.adminReservations]: 'Quản lý đặt bàn',
    [routes.adminUsers]: 'Quản lý người dùng',
    [routes.adminProfile]: 'Hồ sơ cá nhân',
    [routes.unauthorized]: 'Không có quyền truy cập',
    [routes.notFound]: 'Không tìm thấy trang',
  };
  
  return routeTitles[pathname] || 'RestoBot';
};

export const isAdminRoute = (pathname: string): boolean => {
  return pathname.startsWith('/admin');
};

export const isPublicRoute = (pathname: string): boolean => {
  const publicRoutes = [routes.login, routes.register];
  return publicRoutes.includes(pathname);
};