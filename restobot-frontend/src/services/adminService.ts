import { apiClient } from './apiClient';

// ============ ENUMS ============
export enum OrderStatus {
  PENDING = 'pending',
  CONFIRMED = 'confirmed', 
  PREPARING = 'preparing',
  READY = 'ready',
  SERVED = 'served',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled'
}

export enum ReservationStatus {
  PENDING = 'pending',
  CONFIRMED = 'confirmed',
  CANCELLED = 'cancelled',
  COMPLETED = 'completed',
  NO_SHOW = 'no_show'
}

export enum TableStatus {
  AVAILABLE = 'available',
  OCCUPIED = 'occupied',
  RESERVED = 'reserved',
  MAINTENANCE = 'maintenance'
}

export enum UserRole {
  CUSTOMER = 'customer',
  STAFF = 'staff',
  MANAGER = 'manager',
  ADMIN = 'admin'
}

// ============ INTERFACES ============
export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface UserCreate {
  username: string;
  email: string;
  full_name: string;
  password: string;
  role?: UserRole;
}

export interface UserUpdate {
  username?: string;
  email?: string;
  full_name?: string;
  role?: UserRole;
  is_active?: boolean;
}

export interface Category {
  id: number;
  name: string;
  description: string;
  is_active: boolean;
  created_at: string;
}

export interface CategoryCreate {
  name: string;
  description?: string;
  is_active?: boolean;
}

export interface MenuItem {
  id: number;
  name: string;
  description: string;
  price: number;
  category_id: number;
  is_available: boolean;
  preparation_time: number;
  image_url?: string;
  created_at: string;
}

export interface MenuItemCreate {
  name: string;
  description?: string;
  price: number;
  category_id: number;
  is_available?: boolean;
  preparation_time?: number;
  image_url?: string;
}

export interface Table {
  id: number;
  table_number: string;
  capacity: number;
  location: string;
  status: TableStatus;
  created_at: string;
}

export interface TableCreate {
  table_number: string;
  capacity: number;
  location?: string;
  status?: TableStatus;
}

export interface Order {
  id: number;
  order_number: string;
  user_id: number;
  table_id?: number;
  status: OrderStatus;
  payment_status: 'pending' | 'paid' | 'refunded';
  total_amount: number;
  created_at: string;
  updated_at: string;
}

export interface OrderCreate {
  table_id?: number;
  items: OrderItem[];
}

export interface OrderItem {
  menu_item_id: number;
  quantity: number;
  special_instructions?: string;
}

export interface Reservation {
  id: number;
  user_id: number;
  table_id: number;
  reservation_date: string;
  party_size: number;
  status: ReservationStatus;
  special_requests?: string;
  created_at: string;
}

export interface ReservationCreate {
  table_id: number;
  reservation_date: string;
  party_size: number;
  special_requests?: string;
}

export interface DailySummary {
  total_orders: number;
  total_revenue: number;
  pending_orders: number;
  completed_orders: number;
}

// ============ AUTHENTICATION SERVICE ============
export const authService = {
  register: (data: UserCreate) =>
    apiClient.post('/api/v1/auth/register', data),
    
  login: (username: string, password: string) =>
    apiClient.post('/api/v1/auth/login', { username, password }),
    
  registerStaff: (data: UserCreate) =>
    apiClient.post('/api/v1/auth/register-staff', data),
};

// ============ USER SERVICE ============
export const userService = {
  getCurrentUser: () =>
    apiClient.get<User>('/api/v1/users/me'),
    
  updateCurrentUser: (data: UserUpdate) =>
    apiClient.put<User>('/api/v1/users/me', data),
    
  getUsers: (skip = 0, limit = 100) =>
    apiClient.get<User[]>('/api/v1/users/', {
      params: { skip, limit }
    }),
    
  getUserById: (userId: number) =>
    apiClient.get<User>(`/api/v1/users/${userId}`),
    
  createUser: (data: UserCreate) => {
    // Use registerStaff for staff, manager, admin roles, regular register for customers
    if (data.role && [UserRole.STAFF, UserRole.MANAGER, UserRole.ADMIN].includes(data.role)) {
      return apiClient.post<User>('/api/v1/auth/register-staff', data);
    } else {
      return apiClient.post<User>('/api/v1/auth/register', data);
    }
  },
    
  updateUser: (userId: number, data: UserUpdate) =>
    apiClient.put<User>(`/api/v1/users/${userId}`, data),
    
  deleteUser: (userId: number) =>
    apiClient.delete(`/api/v1/users/${userId}`),
    
  getStaffUsers: () =>
    apiClient.get<User[]>('/api/v1/users/staff/list'),
};

// ============ MENU SERVICE ============
export const menuService = {
  // Categories
  getCategories: (skip = 0, limit = 100) =>
    apiClient.get<Category[]>('/api/v1/menu/categories/', {
      params: { skip, limit }
    }),
    
  createCategory: (data: CategoryCreate) =>
    apiClient.post<Category>('/api/v1/menu/categories/', data),
    
  getCategoriesWithItems: () =>
    apiClient.get('/api/v1/menu/categories/with-items'),
    
  getCategoryById: (categoryId: number) =>
    apiClient.get<Category>(`/api/v1/menu/categories/${categoryId}`),
    
  updateCategory: (categoryId: number, data: Partial<Category>) =>
    apiClient.put<Category>(`/api/v1/menu/categories/${categoryId}`, data),
    
  deleteCategory: (categoryId: number) =>
    apiClient.delete(`/api/v1/menu/categories/${categoryId}`),
    
  // Menu Items
  getMenuItems: (skip = 0, limit = 100) =>
    apiClient.get<MenuItem[]>('/api/v1/menu/items/', {
      params: { skip, limit }
    }),
    
  createMenuItem: (data: MenuItemCreate) =>
    apiClient.post<MenuItem>('/api/v1/menu/items/', data),
    
  getFeaturedItems: () =>
    apiClient.get<MenuItem[]>('/api/v1/menu/items/featured'),
    
  searchMenuItems: (query: string) =>
    apiClient.get<MenuItem[]>('/api/v1/menu/items/search', {
      params: { query }
    }),
    
  getMenuItemById: (itemId: number) =>
    apiClient.get<MenuItem>(`/api/v1/menu/items/${itemId}`),
    
  updateMenuItem: (itemId: number, data: Partial<MenuItem>) =>
    apiClient.put<MenuItem>(`/api/v1/menu/items/${itemId}`, data),
    
  deleteMenuItem: (itemId: number) =>
    apiClient.delete(`/api/v1/menu/items/${itemId}`),
};

// ============ TABLE SERVICE ============
export const tableService = {
  getTables: (skip = 0, limit = 100) =>
    apiClient.get<Table[]>('/api/v1/tables/', {
      params: { skip, limit }
    }),
    
  createTable: (data: TableCreate) =>
    apiClient.post<Table>('/api/v1/tables/', data),
    
  getAvailableTables: () =>
    apiClient.get<Table[]>('/api/v1/tables/available'),
    
  getTablesByStatus: (status: TableStatus) =>
    apiClient.get<Table[]>(`/api/v1/tables/by-status/${status}`),
    
  getTableById: (tableId: number) =>
    apiClient.get<Table>(`/api/v1/tables/${tableId}`),
    
  updateTable: (tableId: number, data: Partial<Table>) =>
    apiClient.put<Table>(`/api/v1/tables/${tableId}`, data),
    
  deleteTable: (tableId: number) =>
    apiClient.delete(`/api/v1/tables/${tableId}`),
    
  updateTableStatus: (tableId: number, status: TableStatus) =>
    apiClient.patch<Table>(`/api/v1/tables/${tableId}/status`, { status }),
};

// ============ ORDER SERVICE ============
export const orderService = {
  getOrders: (skip = 0, limit = 100) =>
    apiClient.get<Order[]>('/api/v1/orders/orders/', {
      params: { skip, limit }
    }),
    
  createOrder: (data: OrderCreate) =>
    apiClient.post<Order>('/api/v1/orders/orders/', data),
    
  getMyOrders: (skip = 0, limit = 100) =>
    apiClient.get<Order[]>('/api/v1/orders/orders/my', {
      params: { skip, limit }
    }),
    
  getOrderById: (orderId: number) =>
    apiClient.get<Order>(`/api/v1/orders/orders/${orderId}`),
    
  updateOrder: (orderId: number, data: Partial<Order>) =>
    apiClient.put<Order>(`/api/v1/orders/orders/${orderId}`, data),
    
  getDailySummary: () =>
    apiClient.get<DailySummary>('/api/v1/orders/summary/daily'),
};

// ============ RESERVATION SERVICE ============
export const reservationService = {
  getReservations: (skip = 0, limit = 100) =>
    apiClient.get<Reservation[]>('/api/v1/orders/reservations/', {
      params: { skip, limit }
    }),
    
  createReservation: (data: ReservationCreate) =>
    apiClient.post<Reservation>('/api/v1/orders/reservations/', data),
    
  getMyReservations: (skip = 0, limit = 100) =>
    apiClient.get<Reservation[]>('/api/v1/orders/reservations/my', {
      params: { skip, limit }
    }),
    
  getReservationById: (reservationId: number) =>
    apiClient.get<Reservation>(`/api/v1/orders/reservations/${reservationId}`),
    
  updateReservation: (reservationId: number, data: Partial<Reservation>) =>
    apiClient.put<Reservation>(`/api/v1/orders/reservations/${reservationId}`, data),
    
  cancelReservation: (reservationId: number) =>
    apiClient.delete(`/api/v1/orders/reservations/${reservationId}`),
};
