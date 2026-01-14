import { apiClient } from './apiClient';
import { 
  Dish, 
  CreateDishRequest, 
  MenuCategory, 
  PaginatedResponse 
} from '../types';

export class MenuService {
  // Dish management
  async getDishes(params?: {
    page?: number;
    size?: number;
    category_id?: number;
    search?: string;
    is_available?: boolean;
  }): Promise<PaginatedResponse<Dish>> {
    return apiClient.get<PaginatedResponse<Dish>>('/api/v1/menu/items', { params });
  }

  async getDish(id: number): Promise<Dish> {
    return apiClient.get<Dish>(`/api/v1/menu/items/${id}`);
  }

  async createDish(dishData: CreateDishRequest): Promise<Dish> {
    return apiClient.post<Dish>('/api/v1/menu/items', dishData);
  }

  async updateDish(id: number, dishData: Partial<CreateDishRequest>): Promise<Dish> {
    return apiClient.put<Dish>(`/api/v1/menu/items/${id}`, dishData);
  }

  async deleteDish(id: number): Promise<void> {
    return apiClient.delete(`/api/v1/menu/items/${id}`);
  }

  async toggleDishAvailability(id: number): Promise<Dish> {
    return apiClient.patch<Dish>(`/api/v1/menu/items/${id}/toggle-availability`);
  }

  // Category management
  async getCategories(params?: {
    page?: number;
    size?: number;
    is_active?: boolean;
  }): Promise<PaginatedResponse<MenuCategory>> {
    return apiClient.get<PaginatedResponse<MenuCategory>>('/api/v1/menu/categories', { params });
  }

  async getCategory(id: number): Promise<MenuCategory> {
    return apiClient.get<MenuCategory>(`/api/v1/menu/categories/${id}`);
  }

  async createCategory(categoryData: Omit<MenuCategory, 'id'>): Promise<MenuCategory> {
    return apiClient.post<MenuCategory>('/api/v1/menu/categories', categoryData);
  }

  async updateCategory(id: number, categoryData: Partial<MenuCategory>): Promise<MenuCategory> {
    return apiClient.put<MenuCategory>(`/api/v1/menu/categories/${id}`, categoryData);
  }

  async deleteCategory(id: number): Promise<void> {
    return apiClient.delete(`/api/v1/menu/categories/${id}`);
  }

  // Public methods (không cần auth)
  async getPublicMenu(): Promise<{
    categories: MenuCategory[];
    dishes: Dish[];
  }> {
    return apiClient.get('/api/v1/menu/public');
  }

  async getPopularDishes(limit: number = 10): Promise<Dish[]> {
    return apiClient.get<Dish[]>(`/api/v1/menu/popular?limit=${limit}`);
  }

  async getFeaturedDishes(): Promise<Dish[]> {
    return apiClient.get<Dish[]>('/api/v1/menu/featured');
  }

  async searchDishes(query: string): Promise<Dish[]> {
    return apiClient.get<Dish[]>(`/api/v1/menu/search?q=${encodeURIComponent(query)}`);
  }
}

export const menuService = new MenuService();