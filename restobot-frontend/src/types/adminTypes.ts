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
  RESERVED = 'reserved'
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
  password?: string;
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
  is_featured: boolean;
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
  is_featured?: boolean;
  preparation_time?: number;
  image_url?: string;
}

export interface PaginatedMenuResponse {
  items: MenuItem[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface PaginatedCategoryResponse {
  items: Category[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface PaginatedOrderResponse {
  items: Order[];
  total: number;
  skip: number;
  limit: number;
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

export interface TablesResponse {
  tables: Table[];
  total: number;
}

export interface Order {
  id: number;
  order_number: string;
  customer_id?: number;
  table_id?: number;
  status: OrderStatus;
  payment_status: 'pending' | 'paid' | 'refunded';
  total_amount: number;
  created_at: string;
  updated_at: string;
  // Additional info for admin view
  customer_name?: string;
  customer_email?: string;
  table_number?: string;
  order_items?: OrderItemDetail[];
}

export interface OrderItem {
  menu_item_id: number;
  quantity: number;
  special_instructions?: string;
}

export interface OrderItemDetail extends OrderItem {
  item_name?: string;
  item_price?: number;
  item_image?: string;
  unit_price: number;
  total_price: number;
}

export interface OrderCreate {
  table_id?: number;
  items: OrderItem[];
}

export interface Reservation {
  id: number;
  user_id: number;
  customer_name: string;
  customer_email: string;
  customer_phone?: string;
  table_id: number;
  table_number: string;
  table_capacity: number;
  table_location?: string;
  reservation_date: string;
  party_size: number;
  status: ReservationStatus;
  special_requests?: string;
  notes?: string;
  created_at: string;
}

export interface ReservationCreate {
  table_id: number;
  reservation_date: string;
  party_size: number;
  special_requests?: string;
}

export interface PaginatedReservationResponse {
  items: Reservation[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface DailySummary {
  total_orders: number;
  total_revenue: number;
  pending_orders: number;
  completed_orders: number;
}

export interface DashboardStats {
  // Orders
  total_orders: number;
  pending_orders: number;
  completed_orders: number;
  total_revenue: number;
  
  // Tables
  total_tables: number;
  available_tables: number;
  occupied_tables: number;
  reserved_tables: number;
  
  // Users
  total_customers: number;
  total_staff: number;
  
  // Menu
  total_menu_items: number;
  available_menu_items: number;
  
  // Reservations
  total_reservations: number;
  pending_reservations: number;
  confirmed_reservations: number;
  
  // Recent activity
  recent_orders: RecentOrder[];
  recent_reservations: RecentReservation[];
  popular_items: PopularItem[];
}

export interface RecentOrder {
  id: number;
  order_number: string;
  status: string;
  total_amount: number;
  created_at: string;
  customer_name: string;
  table_number: string;
}

export interface RecentReservation {
  id: number;
  reservation_date: string;
  party_size: number;
  status: string;
  customer_name: string;
  table_number: string;
}

export interface PopularItem {
  id: number;
  name: string;
  price: number;
  total_ordered: number;
}