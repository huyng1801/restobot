import { apiClient } from './apiClient';
import { 
  Table, 
  Reservation, 
  CreateReservationRequest, 
  PaginatedResponse 
} from '../types';

export class TableService {
  // Table management
  async getTables(params?: {
    page?: number;
    size?: number;
    status?: Table['current_status'];
    capacity?: number;
  }): Promise<PaginatedResponse<Table>> {
    return apiClient.get<PaginatedResponse<Table>>('/api/v1/tables', { params });
  }

  async getTable(id: number): Promise<Table> {
    return apiClient.get<Table>(`/api/v1/tables/${id}`);
  }

  async createTable(tableData: Omit<Table, 'id' | 'current_status'>): Promise<Table> {
    return apiClient.post<Table>('/api/v1/tables', {
      ...tableData,
      current_status: 'available'
    });
  }

  async updateTable(id: number, tableData: Partial<Table>): Promise<Table> {
    return apiClient.put<Table>(`/api/v1/tables/${id}`, tableData);
  }

  async deleteTable(id: number): Promise<void> {
    return apiClient.delete(`/api/v1/tables/${id}`);
  }

  async updateTableStatus(id: number, updateData: { status: Table['current_status'] }): Promise<Table> {
    return apiClient.patch<Table>(`/api/v1/tables/${id}/status`, updateData);
  }

  // Table status management
  async checkIn(tableId: number, orderId?: number): Promise<Table> {
    return apiClient.post<Table>(`/api/v1/tables/${tableId}/check-in`, { order_id: orderId });
  }

  async checkOut(tableId: number): Promise<Table> {
    return apiClient.post<Table>(`/api/v1/tables/${tableId}/check-out`);
  }

  async completeTableCleaning(tableId: number): Promise<Table> {
    return apiClient.post<Table>(`/api/v1/tables/${tableId}/cleaning-complete`);
  }

  async syncTableStatuses(): Promise<Table[]> {
    return apiClient.post<Table[]>('/api/v1/tables/sync-statuses');
  }

  async getStatusSummary(): Promise<{
    status_summary: {
      available: number;
      occupied: number;
      reserved: number;
      cleaning: number;
      maintenance: number;
    };
    timestamp: string;
  }> {
    return apiClient.get('/api/v1/tables/status-summary');
  }

  // Available tables
  async getAvailableTables(params?: {
    date?: string;
    time?: string;
    capacity?: number;
  }): Promise<Table[]> {
    return apiClient.get<Table[]>('/api/v1/tables/available', { params });
  }

  // Reservation management
  async getReservations(params?: {
    page?: number;
    size?: number;
    date?: string;
    status?: Reservation['status'];
    customer_phone?: string;
  }): Promise<PaginatedResponse<Reservation>> {
    return apiClient.get<PaginatedResponse<Reservation>>('/api/v1/orders/reservations', { params });
  }

  async getReservation(id: number): Promise<Reservation> {
    return apiClient.get<Reservation>(`/api/v1/orders/reservations/${id}`);
  }

  async createReservation(reservationData: CreateReservationRequest): Promise<Reservation> {
    return apiClient.post<Reservation>('/api/v1/orders/reservations', reservationData);
  }

  async updateReservation(id: number, reservationData: Partial<CreateReservationRequest>): Promise<Reservation> {
    return apiClient.put<Reservation>(`/api/v1/orders/reservations/${id}`, reservationData);
  }

  async updateReservationStatus(id: number, status: Reservation['status']): Promise<Reservation> {
    return apiClient.patch<Reservation>(`/api/v1/orders/reservations/${id}/status`, { status });
  }

  async cancelReservation(id: number): Promise<Reservation> {
    return this.updateReservationStatus(id, 'cancelled');
  }

  async confirmReservation(id: number): Promise<Reservation> {
    return this.updateReservationStatus(id, 'confirmed');
  }

  // Public booking (for customers)
  async checkAvailability(params: {
    date: string;
    time: string;
    guests: number;
  }): Promise<{
    available: boolean;
    suggested_times?: string[];
    available_tables: Table[];
  }> {
    return apiClient.get('/api/v1/tables/check-availability', { params });
  }

  async bookTable(reservationData: CreateReservationRequest): Promise<Reservation> {
    return apiClient.post<Reservation>('/api/v1/tables/book', reservationData);
  }

  // Today's reservations
  async getTodayReservations(): Promise<Reservation[]> {
    const today = new Date().toISOString().split('T')[0];
    const response = await this.getReservations({ date: today, size: 100 });
    return response.data;
  }

  // Upcoming reservations
  async getUpcomingReservations(days: number = 7): Promise<Reservation[]> {
    const startDate = new Date().toISOString().split('T')[0];
    const endDate = new Date(Date.now() + days * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    
    return apiClient.get<Reservation[]>('/api/v1/orders/reservations/upcoming', {
      params: { start_date: startDate, end_date: endDate }
    });
  }
}

export const tableService = new TableService();