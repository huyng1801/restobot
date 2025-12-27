import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { toast } from 'react-toastify';

/**
 * API client configuration
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://103.56.160.107:8000';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors globally
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error) => {
    // Handle common errors
    if (error.response) {
      const { status, data } = error.response;
      
      switch (status) {
        case 401:
          // Unauthorized - redirect to login
          localStorage.removeItem('access_token');
          localStorage.removeItem('user');
          window.location.href = '/login';
          toast.error('Phiên đăng nhập đã hết hạn');
          break;
          
        case 403:
          toast.error('Bạn không có quyền thực hiện hành động này');
          break;
          
        case 404:
          toast.error('Không tìm thấy tài nguyên yêu cầu');
          break;
          
        case 422:
          // Validation errors
          if (data.detail && Array.isArray(data.detail)) {
            const errorMessage = data.detail
              .map((err: any) => `${err.loc.join('.')}: ${err.msg}`)
              .join(', ');
            toast.error(`Lỗi dữ liệu: ${errorMessage}`);
          } else if (data.detail) {
            toast.error(data.detail);
          }
          break;
          
        case 500:
          toast.error('Lỗi máy chủ nội bộ');
          break;
          
        default:
          if (data.detail) {
            toast.error(data.detail);
          } else {
            toast.error('Đã xảy ra lỗi không xác định');
          }
      }
    } else if (error.request) {
      // Network error
      toast.error('Không thể kết nối đến máy chủ');
    } else {
      toast.error('Đã xảy ra lỗi không xác định');
    }
    
    return Promise.reject(error);
  }
);

/**
 * API request methods
 */

export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export const api = {
  // GET request
  get: async <T>(url: string, config?: AxiosRequestConfig): Promise<T> => {
    const response = await apiClient.get<T>(url, config);
    return response.data;
  },

  // POST request
  post: async <T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => {
    const response = await apiClient.post<T>(url, data, config);
    return response.data;
  },

  // PUT request
  put: async <T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => {
    const response = await apiClient.put<T>(url, data, config);
    return response.data;
  },

  // PATCH request
  patch: async <T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => {
    const response = await apiClient.patch<T>(url, data, config);
    return response.data;
  },

  // DELETE request
  delete: async <T>(url: string, config?: AxiosRequestConfig): Promise<T> => {
    const response = await apiClient.delete<T>(url, config);
    return response.data;
  },

  // Upload file
  upload: async <T>(url: string, file: File, onProgress?: (progressEvent: any) => void): Promise<T> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<T>(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: onProgress,
    });

    return response.data;
  },
};

/**
 * API endpoints
 */

export const endpoints = {
  auth: {
    login: '/api/v1/auth/login',
    register: '/api/v1/auth/register',
    registerStaff: '/api/v1/auth/register-staff',
    me: '/api/v1/users/me',
  },
  users: {
    list: '/api/v1/users/',
    create: '/api/v1/users/',
    me: '/api/v1/users/me',
    updateMe: '/api/v1/users/me',
    changePassword: '/api/v1/users/me/change-password',
    get: (id: number) => `/api/v1/users/${id}`,
    update: (id: number) => `/api/v1/users/${id}`,
    delete: (id: number) => `/api/v1/users/${id}`,
    staff: '/api/v1/users/staff/list',
  },
  menu: {
    categories: '/api/v1/menu/categories/',
    categoriesWithItems: '/api/v1/menu/categories/with-items',
    items: '/api/v1/menu/items/',
    featuredItems: '/api/v1/menu/items/featured',
    createCategory: '/api/v1/menu/categories/',
    createItem: '/api/v1/menu/items/',
    getCategory: (id: number) => `/api/v1/menu/categories/${id}`,
    getItem: (id: number) => `/api/v1/menu/items/${id}`,
    updateCategory: (id: number) => `/api/v1/menu/categories/${id}`,
    updateItem: (id: number) => `/api/v1/menu/items/${id}`,
    deleteCategory: (id: number) => `/api/v1/menu/categories/${id}`,
    deleteItem: (id: number) => `/api/v1/menu/items/${id}`,
  },
  tables: {
    list: '/api/v1/tables/',
    create: '/api/v1/tables/',
    available: '/api/v1/tables/available',
    byStatus: (status: string) => `/api/v1/tables/by-status/${status}`,
    get: (id: number) => `/api/v1/tables/${id}`,
    update: (id: number) => `/api/v1/tables/${id}`,
    delete: (id: number) => `/api/v1/tables/${id}`,
    updateStatus: (id: number) => `/api/v1/tables/${id}/status`,
  },
  orders: {
    reservations: '/api/v1/orders/reservations/',
    createReservation: '/api/v1/orders/reservations/',
    myReservations: '/api/v1/orders/reservations/my',
    getReservation: (id: number) => `/api/v1/orders/reservations/${id}`,
    updateReservation: (id: number) => `/api/v1/orders/reservations/${id}`,
    cancelReservation: (id: number) => `/api/v1/orders/reservations/${id}`,
    orders: '/api/v1/orders/orders/',
    createOrder: '/api/v1/orders/orders/',
    myOrders: '/api/v1/orders/orders/my',
    getOrder: (id: number) => `/api/v1/orders/orders/${id}`,
    updateOrder: (id: number) => `/api/v1/orders/orders/${id}`,
    dailySummary: '/api/v1/orders/summary/daily',
  },
  chat: {
    webhook: '/webhook',
    message: '/chat',
  },
  health: '/health',
  root: '/',
};

export default apiClient;