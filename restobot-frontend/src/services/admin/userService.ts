import { apiClient } from '../apiClient';
import { User, UserCreate, UserUpdate, UserRole } from '../../types/adminTypes';

export const userService = {
  getCurrentUser: () =>
    apiClient.get<User>('/api/v1/users/me'),
    
  updateCurrentUser: (data: UserUpdate) =>
    apiClient.put<User>('/api/v1/users/me', data),
    
  getUsers: (skip = 0, limit = 100) =>
    apiClient.get<User[]>('/api/v1/users/', {
      params: { skip, limit }
    }),
    
  getUserById: (userId: number) =>
    apiClient.get<User>(`/api/v1/users/${userId}`),
    
  createUser: (data: UserCreate) => {
    // Use registerStaff for staff, manager, admin roles, regular register for customers
    if (data.role && [UserRole.STAFF, UserRole.MANAGER, UserRole.ADMIN].includes(data.role)) {
      return apiClient.post<User>('/api/v1/auth/register-staff', data);
    } else {
      return apiClient.post<User>('/api/v1/auth/register', data);
    }
  },
    
  updateUser: (userId: number, data: UserUpdate) =>
    apiClient.put<User>(`/api/v1/users/${userId}`, data),
    
  deleteUser: (userId: number) =>
    apiClient.delete(`/api/v1/users/${userId}`),
    
  getStaffUsers: () =>
    apiClient.get<User[]>('/api/v1/users/staff/list'),
};