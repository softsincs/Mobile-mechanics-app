// MobileMechanic API client — talks to the Django backend.
// Configure via VITE_API_BASE_URL (e.g. https://api.mobilemechanic.example).

const FALLBACK = "http://localhost:8000";
export const API_BASE_URL =
  (typeof import.meta !== "undefined" && (import.meta as any).env?.VITE_API_BASE_URL) || FALLBACK;

const TOKEN_KEY = "mm_auth_token";

export const auth = {
  get token() {
    if (typeof window === "undefined") return null;
    return window.localStorage.getItem(TOKEN_KEY);
  },
  set(token: string) {
    if (typeof window !== "undefined") window.localStorage.setItem(TOKEN_KEY, token);
  },
  clear() {
    if (typeof window !== "undefined") window.localStorage.removeItem(TOKEN_KEY);
  },
};

export class ApiError extends Error {
  status: number;
  data: unknown;
  constructor(message: string, status: number, data: unknown) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

type Options = {
  method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  body?: unknown;
  headers?: Record<string, string>;
  authed?: boolean;
};

export async function api<T = unknown>(path: string, opts: Options = {}): Promise<T> {
  const { method = "GET", body, headers = {}, authed = false } = opts;
  const url = `${API_BASE_URL}${path.startsWith("/") ? path : `/${path}`}`;

  const finalHeaders: Record<string, string> = {
    Accept: "application/json",
    ...headers,
  };
  if (body !== undefined) finalHeaders["Content-Type"] = "application/json";
  if (authed && auth.token) finalHeaders["Authorization"] = `Token ${auth.token}`;

  const res = await fetch(url, {
    method,
    headers: finalHeaders,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  const text = await res.text();
  const data = text ? safeJson(text) : null;

  if (!res.ok) {
    let msg = `Request failed (${res.status})`;
    
    if (data && typeof data === "object") {
      const errData = data as any;
      // Try different error field names from Django
      if (errData.detail) msg = errData.detail;
      else if (errData.message) msg = errData.message;
      else if (errData.non_field_errors) {
        msg = Array.isArray(errData.non_field_errors) 
          ? errData.non_field_errors[0] 
          : errData.non_field_errors;
      }
      // If it's a field error, try to extract first field error
      else {
        const fields = Object.keys(errData);
        if (fields.length > 0) {
          const field = fields[0];
          const errors = errData[field];
          msg = Array.isArray(errors) ? `${field}: ${errors[0]}` : `${field}: ${errors}`;
        }
      }
    }
    
    throw new ApiError(String(msg), res.status, data);
  }

  return data as T;
}

function safeJson(text: string) {
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

// Types
export interface User {
  id: number;
  phone_number: string;
  email: string;
  first_name: string;
  last_name: string;
  avatar?: string;
  is_mechanic: boolean;
}

export interface AuthResponse {
  token: string;
  user_id: number;
  user?: User;
}

export interface Service {
  id: number;
  name: string;
  description?: string;
  price?: number;
  category?: string;
}

export interface Mechanic {
  id: number;
  user: User;
  specialization?: string;
  rating?: number;
  reviews_count?: number;
  is_available?: boolean;
  hourly_rate?: number;
  location?: string;
}

export interface Booking {
  id: number;
  service: Service | number;
  mechanic: Mechanic | number;
  user: User | number;
  description: string;
  location: string;
  status: "pending" | "accepted" | "in-progress" | "completed" | "cancelled";
  created_at?: string;
  updated_at?: string;
  scheduled_date?: string;
  total_price?: number;
}

export interface Notification {
  id: number;
  user: number;
  title: string;
  message: string;
  type: string;
  read: boolean;
  created_at: string;
}

export interface Review {
  id: number;
  mechanic: Mechanic | number;
  user: User | number;
  booking: Booking | number;
  rating: number;
  comment: string;
  created_at: string;
}

export interface JobOffer {
  id: number;
  mechanic: Mechanic | number;
  booking: Booking | number;
  price: number;
  estimated_duration?: string;
  status: "pending" | "accepted" | "rejected";
  created_at: string;
}

// Endpoints
export const endpoints = {
  // Auth endpoints
  signup: (b: { phone_number: string; email: string; password: string; password_confirm?: string; first_name: string; last_name: string }) =>
    api<AuthResponse>("/api/v1/auth/signup/", { method: "POST", body: b }),
  login: (b: { phone_number: string; password: string }) =>
    api<AuthResponse>("/api/v1/auth/login/", { method: "POST", body: b }),
  profile: () => api<User>("/api/v1/auth/profile/", { authed: true }),
  logout: () => api("/api/v1/auth/logout/", { method: "POST", authed: true }),

  // Services endpoints
  services: () => api<Service[]>("/api/v1/services/", { authed: true }),
  getService: (id: number) => api<Service>(`/api/v1/services/${id}/`, { authed: true }),

  // Categories endpoints
  categories: () => api("/api/v1/categories/", { authed: true }),

  // Mechanics endpoints
  mechanics: () => api<Mechanic[]>("/api/v1/mechanics/", { authed: true }),
  getMechanic: (id: number) => api<Mechanic>(`/api/v1/mechanics/${id}/`, { authed: true }),

  // Bookings endpoints
  bookings: () => api<Booking[]>("/api/v1/bookings/", { authed: true }),
  getBooking: (id: number) => api<Booking>(`/api/v1/bookings/${id}/`, { authed: true }),
  createBooking: (b: { service: number; mechanic: number; description: string; location: string; scheduled_date?: string }) =>
    api<Booking>("/api/v1/bookings/", { method: "POST", body: b, authed: true }),
  updateBooking: (id: number, b: Partial<Booking>) =>
    api<Booking>(`/api/v1/bookings/${id}/`, { method: "PATCH", body: b, authed: true }),
  cancelBooking: (id: number) =>
    api(`/api/v1/bookings/${id}/cancel/`, { method: "POST", authed: true }),

  // Notifications endpoints
  notifications: () => api<Notification[]>("/api/v1/notifications/", { authed: true }),
  getNotification: (id: number) => api<Notification>(`/api/v1/notifications/${id}/`, { authed: true }),
  markNotificationAsRead: (id: number) =>
    api(`/api/v1/notifications/${id}/mark-as-read/`, { method: "POST", authed: true }),

  // Reviews endpoints
  reviews: () => api<Review[]>("/api/v1/reviews/", { authed: true }),
  getMechanicReviews: (mechanicId: number) => api<Review[]>(`/api/v1/reviews/?mechanic=${mechanicId}`, { authed: true }),
  createReview: (b: { mechanic: number; booking: number; rating: number; comment: string }) =>
    api<Review>("/api/v1/reviews/", { method: "POST", body: b, authed: true }),

  // Job Offers endpoints
  jobOffers: () => api<JobOffer[]>("/api/v1/job-offers/", { authed: true }),
  getJobOffer: (id: number) => api<JobOffer>(`/api/v1/job-offers/${id}/`, { authed: true }),
  createJobOffer: (b: { booking: number; price: number; estimated_duration?: string }) =>
    api<JobOffer>("/api/v1/job-offers/", { method: "POST", body: b, authed: true }),
  acceptJobOffer: (id: number) =>
    api(`/api/v1/job-offers/${id}/accept/`, { method: "POST", authed: true }),
  rejectJobOffer: (id: number) =>
    api(`/api/v1/job-offers/${id}/reject/`, { method: "POST", authed: true }),

  // Additional endpoints (from tracking, dispatch, payments, analytics, ratings)
  myBookings: () => api<Booking[]>("/api/v1/bookings/my-bookings/", { authed: true }),
};
