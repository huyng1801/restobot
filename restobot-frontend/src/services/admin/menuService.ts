import { apiClient } from '../apiClient';
import { Category, CategoryCreate, MenuItem, MenuItemCreate, PaginatedMenuResponse } from '../../types/adminTypes';
import { PaginatedCategoryResponse } from '../../types';

export const menuService = {
  // Categories
  getCategories: (skip = 0, limit = 100) =>
    apiClient.get<PaginatedCategoryResponse>('/api/v1/menu/categories/', {
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
  getMenuItems: (skip = 0, limit = 100, categoryId?: number, search?: string, isFeatured?: boolean, isAvailable?: boolean) =>
    apiClient.get<PaginatedMenuResponse>('/api/v1/menu/items/', {
      params: { 
        skip, 
        limit,
        category_id: categoryId,
        available_only: false, // Admin should see all items
        ...(search && { q: search }), // Add search parameter if provided
        ...(isFeatured !== undefined && { is_featured: isFeatured }),
        ...(isAvailable !== undefined && { is_available: isAvailable })
      }
    }),
    
  createMenuItem: (data: MenuItemCreate) =>
    apiClient.post<MenuItem>('/api/v1/menu/items/', data),
    
  getFeaturedItems: () =>
    apiClient.get<MenuItem[]>('/api/v1/menu/items/featured'),
    
  getMenuItemById: (itemId: number) =>
    apiClient.get<MenuItem>(`/api/v1/menu/items/${itemId}`),
    
  updateMenuItem: (itemId: number, data: Partial<MenuItem>) =>
    apiClient.put<MenuItem>(`/api/v1/menu/items/${itemId}`, data),
    
  deleteMenuItem: (itemId: number) =>
    apiClient.delete(`/api/v1/menu/items/${itemId}`),
};