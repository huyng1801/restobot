import { Dish, Order, Reservation, FormErrors } from '../types';

/**
 * Validation schemas for forms
 */

export function validateLogin(values: { username: string; password: string }): FormErrors {
  const errors: FormErrors = {};
  
  if (!values.username) {
    errors.username = 'Tên đăng nhập không được để trống';
  }
  
  if (!values.password) {
    errors.password = 'Mật khẩu không được để trống';
  } else if (values.password.length < 6) {
    errors.password = 'Mật khẩu phải có ít nhất 6 ký tự';
  }
  
  return errors;
}

export function validateRegister(values: {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
  full_name: string;
  phone_number?: string;
}): FormErrors {
  const errors: FormErrors = {};
  
  if (!values.username) {
    errors.username = 'Tên đăng nhập không được để trống';
  } else if (values.username.length < 3) {
    errors.username = 'Tên đăng nhập phải có ít nhất 3 ký tự';
  }
  
  if (!values.email) {
    errors.email = 'Email không được để trống';
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(values.email)) {
    errors.email = 'Email không hợp lệ';
  }
  
  if (!values.password) {
    errors.password = 'Mật khẩu không được để trống';
  } else if (values.password.length < 6) {
    errors.password = 'Mật khẩu phải có ít nhất 6 ký tự';
  }
  
  if (!values.confirmPassword) {
    errors.confirmPassword = 'Vui lòng xác nhận mật khẩu';
  } else if (values.password !== values.confirmPassword) {
    errors.confirmPassword = 'Mật khẩu xác nhận không khớp';
  }
  
  if (!values.full_name) {
    errors.full_name = 'Họ tên không được để trống';
  }
  
  if (values.phone_number && !/^(0|\+84)[3-9][0-9]{8}$/.test(values.phone_number.replace(/\s+/g, ''))) {
    errors.phone_number = 'Số điện thoại không hợp lệ';
  }
  
  return errors;
}

export function validateDish(values: {
  name: string;
  description: string;
  price: number;
  category_id: number;
  preparation_time: number;
}): FormErrors {
  const errors: FormErrors = {};
  
  if (!values.name) {
    errors.name = 'Tên món ăn không được để trống';
  }
  
  if (!values.description) {
    errors.description = 'Mô tả món ăn không được để trống';
  }
  
  if (!values.price || values.price <= 0) {
    errors.price = 'Giá món ăn phải lớn hơn 0';
  }
  
  if (!values.category_id) {
    errors.category_id = 'Vui lòng chọn danh mục';
  }
  
  if (!values.preparation_time || values.preparation_time <= 0) {
    errors.preparation_time = 'Thời gian chuẩn bị phải lớn hơn 0';
  }
  
  return errors;
}

export function validateReservation(values: {
  customer_name: string;
  customer_phone: string;
  number_of_guests: number;
  reservation_date: string;
  reservation_time: string;
}): FormErrors {
  const errors: FormErrors = {};
  
  if (!values.customer_name) {
    errors.customer_name = 'Tên khách hàng không được để trống';
  }
  
  if (!values.customer_phone) {
    errors.customer_phone = 'Số điện thoại không được để trống';
  } else if (!/^(0|\+84)[3-9][0-9]{8}$/.test(values.customer_phone.replace(/\s+/g, ''))) {
    errors.customer_phone = 'Số điện thoại không hợp lệ';
  }
  
  if (!values.number_of_guests || values.number_of_guests <= 0) {
    errors.number_of_guests = 'Số khách phải lớn hơn 0';
  } else if (values.number_of_guests > 20) {
    errors.number_of_guests = 'Số khách không được quá 20 người';
  }
  
  if (!values.reservation_date) {
    errors.reservation_date = 'Vui lòng chọn ngày đặt bàn';
  } else {
    const selectedDate = new Date(values.reservation_date);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    if (selectedDate < today) {
      errors.reservation_date = 'Ngày đặt bàn không được trong quá khứ';
    }
  }
  
  if (!values.reservation_time) {
    errors.reservation_time = 'Vui lòng chọn giờ đặt bàn';
  } else {
    const [hour] = values.reservation_time.split(':').map(Number);
    if (hour < 10 || hour >= 22) {
      errors.reservation_time = 'Giờ đặt bàn phải trong khoảng 10:00 - 22:00';
    }
  }
  
  return errors;
}

export function validateTable(values: {
  table_number: string;
  capacity: number;
  location?: string;
}): FormErrors {
  const errors: FormErrors = {};
  
  if (!values.table_number) {
    errors.table_number = 'Số bàn không được để trống';
  }
  
  if (!values.capacity || values.capacity <= 0) {
    errors.capacity = 'Sức chứa phải lớn hơn 0';
  } else if (values.capacity > 20) {
    errors.capacity = 'Sức chứa không được quá 20 người';
  }
  
  return errors;
}

export function validateCategory(values: {
  name: string;
  description?: string;
  display_order: number;
}): FormErrors {
  const errors: FormErrors = {};
  
  if (!values.name) {
    errors.name = 'Tên danh mục không được để trống';
  }
  
  if (values.display_order < 0) {
    errors.display_order = 'Thứ tự hiển thị không được âm';
  }
  
  return errors;
}

/**
 * Business logic validations
 */

export function canEditOrder(order: Order): boolean {
  return ['pending', 'confirmed'].includes(order.status);
}

export function canCancelOrder(order: Order): boolean {
  return ['pending', 'confirmed', 'preparing'].includes(order.status);
}

export function canEditReservation(reservation: Reservation): boolean {
  return ['pending', 'confirmed'].includes(reservation.status);
}

export function canCancelReservation(reservation: Reservation): boolean {
  return ['pending', 'confirmed'].includes(reservation.status);
}

export function isReservationUpcoming(reservation: Reservation): boolean {
  const reservationDateTime = new Date(`${reservation.reservation_date}T${reservation.reservation_time}`);
  const now = new Date();
  return reservationDateTime > now;
}

export function isOrderActive(order: Order): boolean {
  return !['completed', 'cancelled'].includes(order.status);
}

export function getDishAvailabilityColor(dish: Dish): 'success' | 'error' | 'warning' {
  if (!dish.is_available) return 'error';
  return 'success';
}

export function getOrderStatusColor(status: Order['status']): 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' {
  switch (status) {
    case 'pending': return 'warning';
    case 'confirmed': return 'info';
    case 'preparing': return 'primary';
    case 'ready': return 'secondary';
    case 'served': return 'success';
    case 'completed': return 'success';
    case 'cancelled': return 'error';
    default: return 'default';
  }
}

export function getReservationStatusColor(status: Reservation['status']): 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' {
  switch (status) {
    case 'pending': return 'warning';
    case 'confirmed': return 'success';
    case 'completed': return 'success';
    case 'cancelled': return 'error';
    default: return 'default';
  }
}