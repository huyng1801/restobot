import { apiClient } from '../apiClient';
import { Category, CategoryCreate, PaginatedCategoryResponse } from '../../types';

export const categoryService = {
  getCategories: (skip = 0, limit = 100, search = '') =>
    apiClient.get<PaginatedCategoryResponse>('/api/v1/menu/categories/', {
      params: { skip, limit, q: search }
    }),
    
  createCategory: (data: CategoryCreate) =>
    apiClient.post<Category>('/api/v1/menu/categories/', data),
    
  getCategoryById: (categoryId: number) =>
    apiClient.get<Category>(`/api/v1/menu/categories/${categoryId}`),
    
  updateCategory: (categoryId: number, data: Partial<Category>) =>
    apiClient.put<Category>(`/api/v1/menu/categories/${categoryId}`, data),
    
  deleteCategory: (categoryId: number) =>
    apiClient.delete(`/api/v1/menu/categories/${categoryId}`),
};