import { apiClient } from './apiClient';
import { 
  Order, 
  CreateOrderRequest, 
  OrderItem, 
  PaginatedResponse 
} from '../types';

export class OrderService {
  // Order management
  async getOrders(params?: {
    page?: number;
    size?: number;
    status?: Order['status'];
    order_type?: Order['order_type'];
    customer_id?: number;
    table_id?: number;
    date_from?: string;
    date_to?: string;
  }): Promise<PaginatedResponse<Order>> {
    return apiClient.get<PaginatedResponse<Order>>('/orders', { params });
  }

  async getOrder(id: number): Promise<Order> {
    return apiClient.get<Order>(`/orders/${id}`);
  }

  async createOrder(orderData: CreateOrderRequest): Promise<Order> {
    return apiClient.post<Order>('/orders', orderData);
  }

  async updateOrder(id: number, orderData: Partial<CreateOrderRequest>): Promise<Order> {
    return apiClient.put<Order>(`/orders/${id}`, orderData);
  }

  async updateOrderStatus(id: number, status: Order['status']): Promise<Order> {
    return apiClient.patch<Order>(`/orders/${id}/status`, { status });
  }

  async cancelOrder(id: number): Promise<Order> {
    return this.updateOrderStatus(id, 'cancelled');
  }

  // Order items management
  async addOrderItem(orderId: number, item: Omit<OrderItem, 'id' | 'dish' | 'subtotal'>): Promise<Order> {
    return apiClient.post<Order>(`/orders/${orderId}/items`, item);
  }

  async updateOrderItem(orderId: number, itemId: number, item: Partial<OrderItem>): Promise<Order> {
    return apiClient.put<Order>(`/orders/${orderId}/items/${itemId}`, item);
  }

  async removeOrderItem(orderId: number, itemId: number): Promise<Order> {
    return apiClient.delete<Order>(`/orders/${orderId}/items/${itemId}`);
  }

  // Kitchen & Service operations
  async markOrderAsConfirmed(id: number): Promise<Order> {
    return this.updateOrderStatus(id, 'confirmed');
  }

  async markOrderAsPreparing(id: number): Promise<Order> {
    return this.updateOrderStatus(id, 'preparing');
  }

  async markOrderAsReady(id: number): Promise<Order> {
    return this.updateOrderStatus(id, 'ready');
  }

  async markOrderAsServed(id: number): Promise<Order> {
    return this.updateOrderStatus(id, 'served');
  }

  async markOrderAsCompleted(id: number): Promise<Order> {
    return this.updateOrderStatus(id, 'completed');
  }

  // Customer order tracking
  async getCustomerOrders(customerId: number): Promise<Order[]> {
    const response = await this.getOrders({ customer_id: customerId, size: 100 });
    return response.data;
  }

  async getActiveOrders(): Promise<Order[]> {
    const response = await this.getOrders({ 
      size: 100,
      // Lấy orders có status không phải completed hoặc cancelled
    });
    return response.data.filter(order => 
      !['completed', 'cancelled'].includes(order.status)
    );
  }

  // Today's orders
  async getTodayOrders(): Promise<Order[]> {
    const today = new Date().toISOString().split('T')[0];
    const response = await this.getOrders({ 
      date_from: today, 
      date_to: today, 
      size: 1000 
    });
    return response.data;
  }

  // Order statistics
  async getOrderStats(params?: {
    date_from?: string;
    date_to?: string;
  }): Promise<{
    total_orders: number;
    total_revenue: number;
    avg_order_value: number;
    orders_by_status: Record<Order['status'], number>;
    orders_by_type: Record<Order['order_type'], number>;
  }> {
    return apiClient.get('/orders/stats', { params });
  }

  // Calculate order total
  calculateOrderTotal(items: OrderItem[]): number {
    return items.reduce((total, item) => total + (item.unit_price * item.quantity), 0);
  }

  // Create quick order (for walk-in customers)
  async createQuickOrder(tableId: number, items: Omit<OrderItem, 'id' | 'dish' | 'subtotal'>[]): Promise<Order> {
    return this.createOrder({
      table_id: tableId,
      items,
      order_type: 'dine_in'
    });
  }
}

export const orderService = new OrderService();