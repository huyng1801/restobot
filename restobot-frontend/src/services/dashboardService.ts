import { apiClient } from './apiClient';
import { DashboardStats } from '../types';

export class DashboardService {
  async getDashboardStats(): Promise<DashboardStats> {
    return apiClient.get<DashboardStats>('/api/v1/dashboard/stats');
  }

  async getRevenueByPeriod(params: {
    period: 'day' | 'week' | 'month' | 'year';
    start_date?: string;
    end_date?: string;
  }): Promise<Array<{
    date: string;
    revenue: number;
    orders: number;
  }>> {
    return apiClient.get('/api/v1/dashboard/revenue', { params });
  }

  async getPopularDishesStats(params?: {
    limit?: number;
    period?: 'day' | 'week' | 'month';
  }): Promise<Array<{
    dish_id: number;
    dish_name: string;
    order_count: number;
    revenue: number;
  }>> {
    return apiClient.get('/api/v1/dashboard/popular-dishes', { params });
  }

  async getTableUtilization(): Promise<Array<{
    table_id: number;
    table_number: string;
    utilization_rate: number;
    total_reservations: number;
  }>> {
    return apiClient.get('/api/v1/dashboard/table-utilization');
  }

  async getCustomerStats(): Promise<{
    total_customers: number;
    new_customers_today: number;
    returning_customers: number;
    avg_order_value: number;
  }> {
    return apiClient.get('/api/v1/dashboard/customer-stats');
  }

  async getOrderTrends(days: number = 30): Promise<Array<{
    date: string;
    orders: number;
    revenue: number;
    avg_order_value: number;
  }>> {
    return apiClient.get(`/api/v1/dashboard/order-trends?days=${days}`);
  }
}

export const dashboardService = new DashboardService();