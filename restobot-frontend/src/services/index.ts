// Import all services
import { authService, AuthService } from './authService';
import { menuService, MenuService } from './menuService';
import { tableService, TableService } from './tableService';
import { orderService, OrderService } from './orderService';
import { dashboardService, DashboardService } from './dashboardService';
import { chatService } from './chatService';
import { categoryService } from './admin/categoryService';

// Export all services
export { apiClient } from './apiClient';
export { authService, AuthService } from './authService';
export { menuService, MenuService } from './menuService';
export { tableService, TableService } from './tableService';
export { orderService, OrderService } from './orderService';
export { dashboardService, DashboardService } from './dashboardService';
export { chatService } from './chatService';
export { categoryService } from './admin/categoryService';

// Export for convenience
export const services = {
  auth: authService,
  menu: menuService,
  table: tableService,
  order: orderService,
  dashboard: dashboardService,
  chat: chatService,
  category: categoryService,
};