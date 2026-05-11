# Backend-Frontend Integration Guide

## Overview
The Mobile Mechanic frontend has been successfully integrated with the Django backend APIs. The integration includes:

### ✅ Completed Integration Points

#### 1. **API Client (`lib/api.ts`)**
- Comprehensive API wrapper with authentication support
- Token-based authentication using localStorage
- TypeScript interfaces for all API responses
- Error handling with `ApiError` class
- Base URL configuration via environment variables

#### 2. **Authentication Endpoints**
- `POST /api/v1/auth/signup/` - User registration
- `POST /api/v1/auth/login/` - User login
- `GET /api/v1/auth/profile/` - Get current user profile
- `POST /api/v1/auth/logout/` - User logout

#### 3. **Services Management**
- `GET /api/v1/services/` - Fetch all available services
- Services page now displays real data from backend
- Fallback to mock data if backend is unavailable

#### 4. **Mechanics Listing**
- `GET /api/v1/mechanics/` - Fetch all mechanics
- `GET /api/v1/mechanics/{id}/` - Get specific mechanic
- Mechanics page displays ratings, specialization, and availability
- Individual mechanic cards with review aggregation

#### 5. **Bookings Management**
- `GET /api/v1/bookings/` - List all bookings
- `GET /api/v1/bookings/{id}/` - Get booking details
- `POST /api/v1/bookings/` - Create new booking
- `PATCH /api/v1/bookings/{id}/` - Update booking
- `POST /api/v1/bookings/{id}/cancel/` - Cancel booking
- Dedicated bookings page for authenticated users

#### 6. **Notifications**
- `GET /api/v1/notifications/` - List notifications
- `POST /api/v1/notifications/{id}/mark-as-read/` - Mark as read

#### 7. **Reviews & Ratings**
- `GET /api/v1/reviews/` - List reviews
- `GET /api/v1/reviews/?mechanic={id}` - Get mechanic reviews
- `POST /api/v1/reviews/` - Create review

#### 8. **Job Offers**
- `GET /api/v1/job-offers/` - List job offers
- `POST /api/v1/job-offers/` - Create job offer
- `POST /api/v1/job-offers/{id}/accept/` - Accept offer
- `POST /api/v1/job-offers/{id}/reject/` - Reject offer

### 📦 React Query Hooks (`hooks/use-api.ts`)
All endpoints are wrapped with React Query hooks for:
- Automatic caching
- Loading states
- Error handling
- Mutations with optimistic updates
- Query invalidation on mutations

Available hooks:
- `useProfile()` - Get current user
- `useServices()` - Fetch services
- `useMechanics()` - Fetch mechanics list
- `useMechanic(id)` - Get specific mechanic
- `useMechanicReviews(id)` - Get mechanic reviews
- `useBookings()` - List bookings
- `useMyBookings()` - Current user's bookings
- `useCreateBooking()` - Create booking mutation
- `useUpdateBooking()` - Update booking mutation
- `useCancelBooking()` - Cancel booking mutation
- `useNotifications()` - Fetch notifications
- `useMarkNotificationAsRead()` - Mark notification as read
- `useReviews()` - Fetch reviews
- `useCreateReview()` - Create review mutation
- `useJobOffers()` - Fetch job offers
- `useCreateJobOffer()` - Create job offer mutation
- `useAcceptJobOffer()` - Accept job offer mutation
- `useRejectJobOffer()` - Reject job offer mutation

### 🛣️ Routes Added

#### Public Routes
- `/services` - Services listing (updated to show real data)
- `/mechanics` - Mechanics listing (new)

#### Protected Routes
- `/bookings` - User bookings management (new, requires authentication)

#### Updated Components
- `/login` - Login page (already integrated)
- `/signup` - Signup page (already integrated)
- `Header` - Navigation component (updated with auth UI and bookings link)

## Configuration

### Environment Variables
Create a `.env` file in the `frontened` directory:

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000

# Optional: For production
# VITE_API_BASE_URL=https://api.yourdomain.com
```

### Backend API Base URL
- **Development**: `http://localhost:8000`
- **Production**: Update `VITE_API_BASE_URL` in `.env`

## How to Use

### 1. **Fetch Data in Components**
```typescript
import { useServices, useMechanics } from "@/hooks/use-api";

function MyComponent() {
  const { data: services, isLoading } = useServices();
  
  return (
    <div>
      {isLoading ? <LoadingSpinner /> : services.map(s => <ServiceCard key={s.id} service={s} />)}
    </div>
  );
}
```

### 2. **Make Mutations**
```typescript
import { useCreateBooking } from "@/hooks/use-api";

function BookingForm() {
  const createBooking = useCreateBooking();
  
  const handleSubmit = async (data) => {
    await createBooking.mutateAsync({
      service: data.serviceId,
      mechanic: data.mechanicId,
      description: data.description,
      location: data.location,
    });
  };
  
  return <form onSubmit={handleSubmit}>...</form>;
}
```

### 3. **Handle Authentication**
```typescript
import { auth } from "@/lib/api";

// Check if user is authenticated
if (auth.token) {
  // User is logged in
}

// Clear token (logout)
auth.clear();
```

## Testing the Integration

### Run the Backend
```bash
cd Backened/backend
python manage.py runserver
```

### Run the Frontend
```bash
cd frontened
npm run dev
```

### Test Endpoints
1. Visit `http://localhost:5173` (or your frontend URL)
2. Sign up for a new account
3. Navigate to Services - should show backend data
4. Navigate to Mechanics - should show backend data
5. Create a booking from the bookings page
6. View and manage bookings

## Troubleshooting

### CORS Issues
If you encounter CORS errors, ensure the Django backend has CORS enabled:
```python
# In settings.py
INSTALLED_APPS = [
    ...
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    ...
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
]
```

### API Not Found (404)
- Verify backend is running on `http://localhost:8000`
- Check `VITE_API_BASE_URL` in `.env`
- Verify all Django URLs are properly configured in `backend/mobilemechanic/urls.py`

### Authentication Issues
- Clear browser localStorage: `localStorage.clear()`
- Check token is being stored properly after login
- Verify `Authorization: Token <token>` header is being sent in authenticated requests

## Next Steps

### Potential Enhancements
1. **Real-time Updates**: Add WebSocket support for live notifications
2. **Payment Integration**: Connect to payment gateway for bookings
3. **Map Integration**: Show mechanic locations on map
4. **Live Tracking**: Add real-time booking tracking
5. **Ratings System**: Implement in-app ratings and reviews
6. **Analytics Dashboard**: Add admin analytics page
7. **Push Notifications**: Integrate push notification service

### Upcoming Features to Integrate
- Analytics endpoints (`/api/v1/analytics/`)
- Dispatch endpoints (`/api/v1/dispatch/`)
- Payments endpoints (`/api/v1/payments/`)
- Tracking endpoints (`/api/v1/tracking/`)

## Files Modified/Created

### Created Files
- `/src/hooks/use-api.ts` - React Query hooks
- `/src/routes/mechanics.tsx` - Mechanics listing page
- `/src/routes/bookings.tsx` - Bookings management page

### Modified Files
- `/src/lib/api.ts` - Expanded endpoints and added types
- `/src/routes/services.tsx` - Updated to use real API data
- `/src/components/site/Header.tsx` - Added auth UI and bookings link
- `/src/routes/login.tsx` - Already integrated (no changes needed)
- `/src/routes/signup.tsx` - Already integrated (no changes needed)

## API Documentation

Refer to the backend test file for complete API documentation:
- `Backened/backend/test_apis_simple.py` - Contains all API examples and expected responses
- Backend routes are configured in each app's `urls.py` file
- API versioning: `/api/v1/`
