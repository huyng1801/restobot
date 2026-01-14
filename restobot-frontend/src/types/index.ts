// User & Authentication Types
export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: 'admin' | 'staff' | 'customer';
  is_active: boolean;
  created_at: string;
  updated_at?: string;
  phone?: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  full_name: string;
  phone?: string;
}

export interface UpdateProfileRequest {
  email?: string;
  username?: string;
  full_name?: string;
  phone?: string;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

// Menu & Dish Types
export interface MenuCategory {
  id: number;
  name: string;
  description?: string;
  display_order: number;
  is_active: boolean;
}

// Alternative names for consistency with adminService
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

export interface PaginatedCategoryResponse {
  items: Category[];
  total: number;
  skip: number;
  limit: number;
}

export interface Dish {
  id: number;
  name: string;
  description: string;
  price: number;
  category_id: number;
  category?: MenuCategory;
  image_url?: string;
  is_available: boolean;
  preparation_time: number;
  ingredients?: string[];
  allergens?: string[];
  calories?: number;
  created_at: string;
  updated_at: string;
}

// Alternative name for consistency with adminService
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

export interface CreateDishRequest {
  name: string;
  description: string;
  price: number;
  category_id: number;
  image_url?: string;
  is_available: boolean;
  preparation_time: number;
  ingredients?: string[];
  allergens?: string[];
  calories?: number;
}

// Table & Reservation Types
export interface Table {
  id: number;
  table_number: string;
  capacity: number;
  location?: string;
  is_active: boolean;
  current_status: 'available' | 'occupied' | 'reserved' | 'cleaning' | 'maintenance';
}

export interface Reservation {
  id: number;
  customer_name: string;
  customer_phone: string;
  customer_email?: string;
  table_id?: number;
  table?: Table;
  number_of_guests: number;
  reservation_date: string;
  reservation_time: string;
  status: 'pending' | 'confirmed' | 'completed' | 'cancelled';
  special_requests?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateReservationRequest {
  table_id: number;
  reservation_date: string; // ISO format datetime string
  party_size: number;
  special_requests?: string;
  customer_name: string;
  customer_email: string;
  customer_phone?: string;
}

// Order Types
export interface OrderItem {
  id?: number;
  dish_id: number;
  dish?: Dish;
  quantity: number;
  unit_price: number;
  subtotal: number;
  special_instructions?: string;
}

export interface Order {
  id: number;
  order_number: string;
  customer_id?: number;
  customer?: User;
  table_id?: number;
  table?: Table;
  reservation_id?: number;
  items: OrderItem[];
  total_amount: number;
  payment_status: 'pending' | 'paid' | 'refunded';
  status: 'pending' | 'confirmed' | 'preparing' | 'ready' | 'served' | 'completed' | 'cancelled';
  order_type: 'dine_in' | 'takeaway' | 'delivery';
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateOrderRequest {
  customer_id?: number;
  table_id?: number;
  reservation_id?: number;
  items: Omit<OrderItem, 'id' | 'dish' | 'subtotal'>[];
  order_type: 'dine_in' | 'takeaway' | 'delivery';
  notes?: string;
}

// Chat & Bot Types
export interface ChatMessage {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  isTyping?: boolean;
}

export interface ChatSession {
  id: string;
  user_id?: number;
  messages: ChatMessage[];
  context: {
    last_intent?: string;
    current_order?: OrderItem[];
    pending_reservation?: Partial<CreateReservationRequest>;
    last_mentioned_dish?: string;
    conversation_state?: string;
  };
  created_at: string;
  updated_at: string;
}

export interface BotResponse {
  text: string;
  buttons?: Array<{
    title: string;
    payload: string;
  }>;
  images?: string[];
  quick_replies?: string[];
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: 'success' | 'error';
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// Dashboard & Analytics Types
export interface DailySummary {
  total_orders: number;
  total_revenue: number;
  pending_orders: number;
  completed_orders: number;
}

export interface DashboardStats {
  total_orders_today: number;
  total_revenue_today: number;
  total_reservations_today: number;
  active_tables: number;
  popular_dishes: Array<{
    dish: Dish;
    order_count: number;
  }>;
  recent_orders: Order[];
  recent_reservations: Reservation[];
}

// Form Types
export interface FormErrors {
  [key: string]: string | undefined;
}

export interface LoadingState {
  [key: string]: boolean;
}

// Theme Types
export interface ThemeColors {
  primary: string;
  secondary: string;
  success: string;
  warning: string;
  error: string;
  info: string;
}

// Route Types
export interface RouteConfig {
  path: string;
  component: React.ComponentType<any>;
  exact?: boolean;
  auth?: boolean;
  roles?: User['role'][];
}