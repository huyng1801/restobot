import { apiClient } from '../apiClient';
import { Order, OrderCreate, OrderStatus, DailySummary, DashboardStats, PaginatedOrderResponse } from '../../types/adminTypes';

export const orderService = {
  getOrders: (skip = 0, limit = 100, status?: string, search?: string) =>
    apiClient.get<PaginatedOrderResponse>('/api/v1/orders/orders/', {
      params: { 
        skip, 
        limit,
        ...(status && { status }),
        ...(search && { search })
      }
    }),
    
  createOrder: (data: OrderCreate) =>
    apiClient.post<Order>('/api/v1/orders/orders/', data),
    
  getMyOrders: (skip = 0, limit = 100) =>
    apiClient.get<Order[]>('/api/v1/orders/orders/my', {
      params: { skip, limit }
    }),
    
  getOrderById: (orderId: number) =>
    apiClient.get<Order>(`/api/v1/orders/orders/${orderId}`),
    
  getOrderDetails: (orderId: number) =>
    apiClient.get<Order>(`/api/v1/orders/orders/${orderId}/details`),
    
  updateOrder: (orderId: number, data: Partial<Order>) =>
    apiClient.put<Order>(`/api/v1/orders/orders/${orderId}`, data),
    
  updateOrderStatus: (orderId: number, status: OrderStatus) =>
    apiClient.patch<Order>(`/api/v1/orders/orders/${orderId}/status`, { status }),
    
  getDailySummary: () =>
    apiClient.get<DailySummary>('/api/v1/orders/summary/daily'),
    
  getDashboardStats: () =>
    apiClient.get<DashboardStats>('/api/v1/orders/dashboard/stats'),
};