import { apiClient } from '../apiClient';
import { UserCreate } from '../../types/adminTypes';

export const authService = {
  register: (data: UserCreate) =>
    apiClient.post('/api/v1/auth/register', data),
    
  login: (username: string, password: string) =>
    apiClient.post('/api/v1/auth/login', { username, password }),
    
  registerStaff: (data: UserCreate) =>
    apiClient.post('/api/v1/auth/register-staff', data),
};