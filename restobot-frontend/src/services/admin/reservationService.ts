import { apiClient } from '../apiClient';
import { Reservation, ReservationCreate, PaginatedReservationResponse } from '../../types/adminTypes';

export const reservationService = {
  getReservations: (skip = 0, limit = 100) =>
    apiClient.get<PaginatedReservationResponse>('/api/v1/orders/reservations/', {
      params: { skip, limit }
    }),
    
  createReservation: (data: ReservationCreate) =>
    apiClient.post<Reservation>('/api/v1/orders/reservations/', data),
    
  getMyReservations: (skip = 0, limit = 100) =>
    apiClient.get<Reservation[]>('/api/v1/orders/reservations/my', {
      params: { skip, limit }
    }),
    
  getReservationById: (reservationId: number) =>
    apiClient.get<Reservation>(`/api/v1/orders/reservations/${reservationId}`),
    
  updateReservation: (reservationId: number, data: Partial<Reservation>) =>
    apiClient.put<Reservation>(`/api/v1/orders/reservations/${reservationId}`, data),

  updateReservationStatus: (reservationId: number, status: string) =>
    apiClient.patch<Reservation>(`/api/v1/orders/reservations/${reservationId}/status`, { status }),
    
  cancelReservation: (reservationId: number) =>
    apiClient.delete(`/api/v1/orders/reservations/${reservationId}`),
};