import { apiClient } from '../apiClient';
import { Table, TableCreate, TableStatus, TablesResponse } from '../../types/adminTypes';

export const tableService = {
  getTables: async (skip = 0, limit = 100, status?: TableStatus, search?: string) => {
    try {
      const response = await apiClient.get<TablesResponse | Table[]>('/api/v1/tables/', {
        params: { skip, limit, status, search }
      });
      
      // Handle both new format (TablesResponse) and old format (Table[])
      if (Array.isArray(response)) {
        return {
          tables: response,
          total: response.length
        } as TablesResponse;
      }
      return response as TablesResponse;
    } catch (error) {
      // Fallback to old API format if new format fails
      const response = await apiClient.get<Table[]>('/api/v1/tables/', {
        params: { skip, limit }
      });
      return {
        tables: response,
        total: response.length
      } as TablesResponse;
    }
  },
    
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