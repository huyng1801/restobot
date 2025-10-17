import { api, endpoints } from '../utils/api';
import { User, UpdateProfileRequest, ChangePasswordRequest } from '../types';

export class UserService {
  async getProfile(): Promise<User> {
    return api.get<User>(endpoints.users.me);
  }

  async updateProfile(data: UpdateProfileRequest): Promise<User> {
    return api.put<User>(endpoints.users.me, data);
  }

  async changePassword(data: ChangePasswordRequest): Promise<void> {
    return api.post<void>(endpoints.users.changePassword, data);
  }

  async getUsers(page = 1, limit = 10, search?: string): Promise<{
    items: User[];
    total: number;
    page: number;
    size: number;
    pages: number;
  }> {
    const params = new URLSearchParams({
      skip: ((page - 1) * limit).toString(),
      limit: limit.toString(),
    });

    if (search) {
      params.append('search', search);
    }

    return api.get(`${endpoints.users.list}?${params}`);
  }

  async getUserById(id: number): Promise<User> {
    return api.get<User>(`${endpoints.users.list}/${id}`);
  }

  async updateUser(id: number, data: UpdateProfileRequest): Promise<User> {
    return api.put<User>(`${endpoints.users.list}/${id}`, data);
  }

  async deleteUser(id: number): Promise<void> {
    return api.delete(`${endpoints.users.list}/${id}`);
  }
}

export const userService = new UserService();
export default userService;