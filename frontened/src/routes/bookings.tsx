import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { Plus, Loader2, Calendar, MapPin, Wrench, Clock, X, CheckCircle, AlertCircle } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { useMyBookings, useCreateBooking, useCancelBooking, useServices, useMechanics, ApiError } from "@/hooks/use-api";
import { auth } from "@/lib/api";

export const Route = createFileRoute("/bookings")({
  head: () => ({
    meta: [
      { title: "My Bookings — MobileMechanic" },
      { name: "description", content: "Manage your car service bookings and track mechanics." },
    ],
  }),
  beforeLoad: ({ location }) => {
    if (typeof window !== "undefined" && !auth.token) {
      throw new Error("Not authenticated");
    }
  },
  errorComponent: ({ error, reset }) => {
    if (error.message === "Not authenticated") {
      return <AuthRequiredPage />;
    }
    return (
      <div className="container-page py-16 text-center">
        <p className="text-muted-foreground">An error occurred. Please try again.</p>
      </div>
    );
  },
  component: BookingsPage,
});

function AuthRequiredPage() {
  const navigate = useNavigate();
  return (
    <div className="container-page py-16 text-center">
      <AlertCircle className="mx-auto h-12 w-12 text-amber-600" />
      <h1 className="mt-4 text-2xl font-bold">Sign in required</h1>
      <p className="mt-2 text-muted-foreground">You need to be signed in to view your bookings.</p>
      <button
        onClick={() => navigate({ to: "/login" })}
        className="mt-6 rounded-lg bg-gradient-primary px-6 py-2 font-semibold text-primary-foreground"
      >
        Sign in
      </button>
    </div>
  );
}

function BookingsPage() {
  const navigate = useNavigate();
  const { data: bookings = [], isLoading } = useMyBookings();
  const { data: services = [] } = useServices();
  const { data: mechanics = [] } = useMechanics();
  const [showForm, setShowForm] = useState(false);

  return (
    <div className="container-page py-10">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">My Bookings</h1>
          <p className="mt-1 text-muted-foreground">Track and manage all your service bookings.</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="inline-flex items-center gap-2 rounded-lg bg-gradient-primary px-4 py-2 text-sm font-semibold text-primary-foreground"
        >
          <Plus className="h-4 w-4" /> New booking
        </button>
      </div>

      {showForm && (
        <BookingForm
          services={services}
          mechanics={mechanics}
          onClose={() => setShowForm(false)}
        />
      )}

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-3 text-muted-foreground">Loading bookings...</span>
        </div>
      ) : bookings.length === 0 ? (
        <div className="rounded-lg border border-border bg-surface-elevated p-8 text-center">
          <Calendar className="mx-auto h-12 w-12 text-muted-foreground" />
          <h2 className="mt-4 text-lg font-semibold">No bookings yet</h2>
          <p className="mt-2 text-muted-foreground">Create your first booking to get started.</p>
          <button
            onClick={() => setShowForm(true)}
            className="mt-4 rounded-lg bg-gradient-primary px-4 py-2 text-sm font-semibold text-primary-foreground"
          >
            Create booking
          </button>
        </div>
      ) : (
        <div className="grid gap-4">
          {bookings.map((booking) => (
            <BookingCard key={booking.id} booking={booking} />
          ))}
        </div>
      )}
    </div>
  );
}

function BookingForm({
  services,
  mechanics,
  onClose,
}: {
  services: any[];
  mechanics: any[];
  onClose: () => void;
}) {
  const createMutation = useCreateBooking();
  const [formData, setFormData] = useState({
    service: "",
    mechanic: "",
    description: "",
    location: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.service || !formData.mechanic || !formData.description || !formData.location) {
      toast.error("Please fill in all fields");
      return;
    }
    try {
      await createMutation.mutateAsync({
        service: Number(formData.service),
        mechanic: Number(formData.mechanic),
        description: formData.description,
        location: formData.location,
      });
      onClose();
    } catch (err) {
      // Error is handled by mutation hook
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="w-full max-w-md rounded-lg border border-border bg-background p-6">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-xl font-bold">New Booking</h2>
          <button
            onClick={onClose}
            className="rounded-lg p-1 hover:bg-muted"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-sm font-medium">Service</label>
            <select
              value={formData.service}
              onChange={(e) => setFormData({ ...formData, service: e.target.value })}
              className="mt-1 w-full rounded-lg border border-border bg-surface px-3 py-2"
            >
              <option value="">Select a service</option>
              {services.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-sm font-medium">Mechanic</label>
            <select
              value={formData.mechanic}
              onChange={(e) => setFormData({ ...formData, mechanic: e.target.value })}
              className="mt-1 w-full rounded-lg border border-border bg-surface px-3 py-2"
            >
              <option value="">Select a mechanic</option>
              {mechanics.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.user?.first_name} {m.user?.last_name} - {m.specialization}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-sm font-medium">Location</label>
            <input
              type="text"
              value={formData.location}
              onChange={(e) => setFormData({ ...formData, location: e.target.value })}
              placeholder="Your location"
              className="mt-1 w-full rounded-lg border border-border bg-surface px-3 py-2"
            />
          </div>

          <div>
            <label className="text-sm font-medium">Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Describe the issue or service needed"
              rows={3}
              className="mt-1 w-full rounded-lg border border-border bg-surface px-3 py-2"
            />
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 rounded-lg border border-border px-4 py-2 font-semibold hover:bg-muted"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="flex-1 rounded-lg bg-gradient-primary px-4 py-2 font-semibold text-primary-foreground disabled:opacity-50"
            >
              {createMutation.isPending ? "Creating..." : "Create booking"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function BookingCard({ booking }: { booking: any }) {
  const cancelMutation = useCancelBooking();
  const [showCancelConfirm, setShowCancelConfirm] = useState(false);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "text-green-600 bg-green-50";
      case "in-progress":
        return "text-blue-600 bg-blue-50";
      case "pending":
        return "text-yellow-600 bg-yellow-50";
      case "cancelled":
        return "text-red-600 bg-red-50";
      default:
        return "text-gray-600 bg-gray-50";
    }
  };

  const handleCancel = async () => {
    try {
      await cancelMutation.mutateAsync(booking.id);
      setShowCancelConfirm(false);
    } catch (err) {
      // Error handled by mutation
    }
  };

  const serviceData = typeof booking.service === "object" ? booking.service : { name: "Service" };
  const mechanicData = typeof booking.mechanic === "object" ? booking.mechanic : { user: {} };

  return (
    <div className="rounded-lg border border-border bg-surface-elevated p-6">
      <div className="mb-4 flex items-start justify-between">
        <div>
          <h3 className="text-lg font-semibold">{serviceData.name || "Service"}</h3>
          <p className="text-sm text-muted-foreground">
            {mechanicData.user?.first_name} {mechanicData.user?.last_name}
          </p>
        </div>
        <div
          className={`rounded-full px-3 py-1 text-xs font-semibold ${getStatusColor(
            booking.status
          )}`}
        >
          {booking.status.charAt(0).toUpperCase() + booking.status.slice(1)}
        </div>
      </div>

      <div className="space-y-2 text-sm">
        {booking.scheduled_date && (
          <div className="flex items-center gap-2 text-muted-foreground">
            <Calendar className="h-4 w-4" />
            {new Date(booking.scheduled_date).toLocaleString()}
          </div>
        )}
        <div className="flex items-center gap-2 text-muted-foreground">
          <MapPin className="h-4 w-4" />
          {booking.location}
        </div>
        <div className="flex items-center gap-2 text-muted-foreground">
          <Wrench className="h-4 w-4" />
          {booking.description}
        </div>
        {booking.total_price && (
          <div className="flex items-center gap-2 text-muted-foreground">
            <Clock className="h-4 w-4" />
            Total: ₨ {booking.total_price}
          </div>
        )}
      </div>

      {booking.status === "pending" && (
        <div className="mt-4 flex gap-2">
          <button
            onClick={() => setShowCancelConfirm(true)}
            className="flex items-center gap-1 rounded-lg border border-destructive/20 px-3 py-1.5 text-sm font-medium text-destructive hover:bg-destructive/5"
          >
            <X className="h-4 w-4" /> Cancel
          </button>
        </div>
      )}

      {showCancelConfirm && (
        <div className="mt-4 rounded-lg border border-destructive/20 bg-destructive/5 p-3">
          <p className="text-sm text-destructive">Are you sure you want to cancel this booking?</p>
          <div className="mt-3 flex gap-2">
            <button
              onClick={() => setShowCancelConfirm(false)}
              className="flex-1 rounded-lg border border-border px-3 py-1.5 text-sm font-medium hover:bg-muted"
            >
              No, keep it
            </button>
            <button
              onClick={handleCancel}
              disabled={cancelMutation.isPending}
              className="flex-1 rounded-lg bg-destructive px-3 py-1.5 text-sm font-medium text-white hover:opacity-90 disabled:opacity-50"
            >
              {cancelMutation.isPending ? "Cancelling..." : "Yes, cancel"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
