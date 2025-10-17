import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { User } from '../types';
import { authService } from '../services';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  loading: boolean;
  error: string | null;
  login: (username: string, password: string) => Promise<any>;
  logout: () => Promise<void>;
  register: (userData: any) => Promise<void>;
  checkAuth: () => Promise<void>;
  updateUser: (userData: Partial<User>) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const isAuthenticated = !!user && authService.isAuthenticated();
  const loading = isLoading;

  const checkAuth = async () => {
    try {
      setIsLoading(true);
      
      if (authService.isAuthenticated()) {
        // Kiểm tra user từ localStorage trước
        const cachedUser = authService.getCurrentUserFromStorage();
        if (cachedUser) {
          setUser(cachedUser);
          
          // Sau đó verify với server
          try {
            const currentUser = await authService.getCurrentUser();
            setUser(currentUser);
            localStorage.setItem('user', JSON.stringify(currentUser));
          } catch (error) {
            console.warn('Failed to refresh user data:', error);
            // Vẫn dùng cached user nếu không thể refresh
          }
        } else {
          // Nếu không có cached user, thử lấy từ server
          const currentUser = await authService.getCurrentUser();
          setUser(currentUser);
          localStorage.setItem('user', JSON.stringify(currentUser));
        }
      } else {
        setUser(null);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      setUser(null);
      // Clear invalid tokens
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (username: string, password: string) => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await authService.login({ username, password });
      setUser(response.user);
      return response;
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || err.message || 'Login failed';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      setIsLoading(true);
      await authService.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setIsLoading(false);
    }
  };

  const register = async (userData: any) => {
    try {
      setIsLoading(true);
      setError(null);
      await authService.register(userData);
      // Sau khi register thành công, có thể tự động login
      await login(userData.username, userData.password);
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || err.message || 'Registration failed';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const updateUser = async (userData: Partial<User>) => {
    try {
      setIsLoading(true);
      setError(null);
      // Update user in state directly or via API if available
      if (user) {
        const updatedUser = { ...user, ...userData };
        setUser(updatedUser);
        localStorage.setItem('user', JSON.stringify(updatedUser));
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || err.message || 'Update failed';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    checkAuth();
  }, []);

  const value: AuthContextType = {
    user,
    isAuthenticated,
    isLoading,
    loading,
    error,
    login,
    logout,
    register,
    checkAuth,
    updateUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};