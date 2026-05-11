import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ApiError, auth, endpoints } from "@/lib/api";
import type { Service, Mechanic, Booking, Notification, Review, JobOffer, User } from "@/lib/api";
import { toast } from "sonner";

// ============ Auth Queries ============
export function useProfile() {
  return useQuery({
    queryKey: ["profile"],
    queryFn: () => endpoints.profile(),
    enabled: !!auth.token,
  });
}

// ============ Services Queries ============
export function useServices() {
  return useQuery({
    queryKey: ["services"],
    queryFn: () => endpoints.services(),
  });
}

export function useService(id: number) {
  return useQuery({
    queryKey: ["service", id],
    queryFn: () => endpoints.getService(id),
    enabled: !!id,
  });
}

// ============ Mechanics Queries ============
export function useMechanics() {
  return useQuery({
    queryKey: ["mechanics"],
    queryFn: () => endpoints.mechanics(),
  });
}

export function useMechanic(id: number) {
  return useQuery({
    queryKey: ["mechanic", id],
    queryFn: () => endpoints.getMechanic(id),
    enabled: !!id,
  });
}

export function useMechanicReviews(mechanicId: number) {
  return useQuery({
    queryKey: ["mechanic-reviews", mechanicId],
    queryFn: () => endpoints.getMechanicReviews(mechanicId),
    enabled: !!mechanicId,
  });
}

// ============ Bookings Queries ============
export function useBookings() {
  return useQuery({
    queryKey: ["bookings"],
    queryFn: () => endpoints.bookings(),
    enabled: !!auth.token,
  });
}

export function useMyBookings() {
  return useQuery({
    queryKey: ["my-bookings"],
    queryFn: () => endpoints.myBookings(),
    enabled: !!auth.token,
  });
}

export function useBooking(id: number) {
  return useQuery({
    queryKey: ["booking", id],
    queryFn: () => endpoints.getBooking(id),
    enabled: !!id && !!auth.token,
  });
}

export function useCreateBooking() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Parameters<typeof endpoints.createBooking>[0]) => endpoints.createBooking(data),
    onSuccess: () => {
      toast.success("Booking created successfully!");
      queryClient.invalidateQueries({ queryKey: ["bookings"] });
      queryClient.invalidateQueries({ queryKey: ["my-bookings"] });
    },
    onError: (error: ApiError) => {
      toast.error(error.message || "Failed to create booking");
    },
  });
}

export function useUpdateBooking() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Booking> }) => endpoints.updateBooking(id, data),
    onSuccess: () => {
      toast.success("Booking updated successfully!");
      queryClient.invalidateQueries({ queryKey: ["bookings"] });
      queryClient.invalidateQueries({ queryKey: ["my-bookings"] });
    },
    onError: (error: ApiError) => {
      toast.error(error.message || "Failed to update booking");
    },
  });
}

export function useCancelBooking() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => endpoints.cancelBooking(id),
    onSuccess: () => {
      toast.success("Booking cancelled successfully!");
      queryClient.invalidateQueries({ queryKey: ["bookings"] });
      queryClient.invalidateQueries({ queryKey: ["my-bookings"] });
    },
    onError: (error: ApiError) => {
      toast.error(error.message || "Failed to cancel booking");
    },
  });
}

// ============ Notifications Queries ============
export function useNotifications() {
  return useQuery({
    queryKey: ["notifications"],
    queryFn: () => endpoints.notifications(),
    enabled: !!auth.token,
  });
}

export function useNotification(id: number) {
  return useQuery({
    queryKey: ["notification", id],
    queryFn: () => endpoints.getNotification(id),
    enabled: !!id && !!auth.token,
  });
}

export function useMarkNotificationAsRead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => endpoints.markNotificationAsRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });
}

// ============ Reviews Queries ============
export function useReviews() {
  return useQuery({
    queryKey: ["reviews"],
    queryFn: () => endpoints.reviews(),
    enabled: !!auth.token,
  });
}

export function useCreateReview() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Parameters<typeof endpoints.createReview>[0]) => endpoints.createReview(data),
    onSuccess: () => {
      toast.success("Review posted successfully!");
      queryClient.invalidateQueries({ queryKey: ["reviews"] });
      queryClient.invalidateQueries({ queryKey: ["mechanic-reviews"] });
    },
    onError: (error: ApiError) => {
      toast.error(error.message || "Failed to post review");
    },
  });
}

// ============ Job Offers Queries ============
export function useJobOffers() {
  return useQuery({
    queryKey: ["job-offers"],
    queryFn: () => endpoints.jobOffers(),
    enabled: !!auth.token,
  });
}

export function useJobOffer(id: number) {
  return useQuery({
    queryKey: ["job-offer", id],
    queryFn: () => endpoints.getJobOffer(id),
    enabled: !!id && !!auth.token,
  });
}

export function useCreateJobOffer() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Parameters<typeof endpoints.createJobOffer>[0]) => endpoints.createJobOffer(data),
    onSuccess: () => {
      toast.success("Job offer created!");
      queryClient.invalidateQueries({ queryKey: ["job-offers"] });
    },
    onError: (error: ApiError) => {
      toast.error(error.message || "Failed to create job offer");
    },
  });
}

export function useAcceptJobOffer() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => endpoints.acceptJobOffer(id),
    onSuccess: () => {
      toast.success("Job offer accepted!");
      queryClient.invalidateQueries({ queryKey: ["job-offers"] });
      queryClient.invalidateQueries({ queryKey: ["bookings"] });
    },
    onError: (error: ApiError) => {
      toast.error(error.message || "Failed to accept job offer");
    },
  });
}

export function useRejectJobOffer() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => endpoints.rejectJobOffer(id),
    onSuccess: () => {
      toast.success("Job offer rejected!");
      queryClient.invalidateQueries({ queryKey: ["job-offers"] });
    },
    onError: (error: ApiError) => {
      toast.error(error.message || "Failed to reject job offer");
    },
  });
}
