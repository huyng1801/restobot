import { api, endpoints } from '../utils/api';
import { 
  User, 
  LoginRequest, 
  LoginResponse, 
  RegisterRequest 
} from '../types';

export class AuthService {
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    // For OAuth2PasswordRequestForm, we need to send form data
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://103.56.160.107:8000'}${endpoints.auth.login}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Login failed');
    }

    const tokenData = await response.json();
    
    // Store token temporarily to make authenticated request for user info
    localStorage.setItem('access_token', tokenData.access_token);
    
    try {
      // Get user info using the token
      const userResponse = await api.get<User>(endpoints.auth.me);
      
      // Store user info
      localStorage.setItem('user', JSON.stringify(userResponse));
      
      return {
        access_token: tokenData.access_token,
        token_type: tokenData.token_type,
        user: userResponse,
      };
    } catch (error) {
      // If getting user info fails, remove the token
      localStorage.removeItem('access_token');
      throw error;
    }
  }

  async register(userData: RegisterRequest): Promise<LoginResponse> {
    const response = await api.post<LoginResponse>(endpoints.auth.register, userData);
    
    // Lưu token và user info vào localStorage
    localStorage.setItem('access_token', response.access_token);
    localStorage.setItem('user', JSON.stringify(response.user));
    
    return response;
  }

  async logout(): Promise<void> {
    try {
      // Note: Backend doesn't seem to have a logout endpoint yet
      // await api.post(endpoints.auth.logout);
    } finally {
      // Luôn clear localStorage dù API call có thành công hay không
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
    }
  }

  async getCurrentUser(): Promise<User> {
    return api.get<User>(endpoints.auth.me);
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  }

  getCurrentUserFromStorage(): User | null {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  }

  hasRole(role: User['role']): boolean {
    const user = this.getCurrentUserFromStorage();
    return user?.role === role;
  }

  hasAnyRole(roles: User['role'][]): boolean {
    const user = this.getCurrentUserFromStorage();
    return user ? roles.includes(user.role) : false;
  }
}

export const authService = new AuthService();