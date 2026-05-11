# Quick Start Guide - Backend-Frontend Integration

## Prerequisites
- Node.js 18+ installed
- Python 3.9+ installed
- Backend running on `http://localhost:8000`

## 🚀 Quick Setup

### 1. Start the Backend
```bash
cd Backened/backend
python manage.py runserver
```
This starts Django at `http://localhost:8000`

### 2. Install Frontend Dependencies
```bash
cd frontened
npm install
```

### 3. Start Frontend Development Server
```bash
npm run dev
```
Frontend runs at `http://localhost:5173` (or shown in terminal)

## ✨ Testing the Integration

### Test 1: View Services
1. Open `http://localhost:5173`
2. Click "Services" in navigation
3. You should see services loaded from the backend
4. If not loading, check console for errors

### Test 2: Sign Up
1. Click "Get started" button
2. Fill in the registration form
3. Submit to create account
4. You'll be redirected to login

### Test 3: Log In
1. Click "Sign in" 
2. Enter phone number and password
3. On success:
   - Token saved locally
   - Redirected to home page
   - Header now shows "My Bookings" and user name

### Test 4: Browse Mechanics
1. Click "Mechanics" in navigation
2. See list of mechanics from backend
3. Click on any mechanic to see details

### Test 5: Create a Booking
1. Click "My Bookings" (only visible when logged in)
2. Click "New booking" button
3. Select service, mechanic, location, and description
4. Submit to create booking
5. See booking appear in your bookings list

### Test 6: Manage Bookings
1. In "My Bookings" page
2. Click "Cancel" on any pending booking
3. Confirm cancellation

## 🔧 Environment Setup

The `.env` file is already configured for local development:
```
VITE_API_BASE_URL=http://localhost:8000
```

To change backend URL (for production):
1. Edit `frontened/.env`
2. Update `VITE_API_BASE_URL` to your production backend URL
3. Restart frontend dev server

## 🐛 Troubleshooting

### Frontend can't connect to backend
**Solution:**
1. Verify backend is running: `python manage.py runserver`
2. Check if port 8000 is accessible
3. Verify `VITE_API_BASE_URL=http://localhost:8000` in `.env`

### CORS errors in console
**Solution:**
Ensure Django has CORS configured in `settings.py`:
```python
INSTALLED_APPS = [
    'corsheaders',
    ...
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    ...
]

CORS_ALLOWED_ORIGINS = ["http://localhost:5173"]
```

### Login not working
**Solution:**
1. Check backend API: `curl http://localhost:8000/api/v1/auth/login/` -X POST
2. Verify credentials are correct
3. Check browser console for error messages
4. Try clearing localStorage: `localStorage.clear()`

### Services/Mechanics not loading
**Solution:**
1. Check if backend has data in database
2. Run backend test: `python test_apis_simple.py`
3. Check network tab in browser dev tools
4. Verify token is present for authenticated endpoints

## 📝 API Integration Summary

### What's Working
✅ User authentication (signup/login/logout)
✅ Profile management  
✅ Services listing
✅ Mechanics listing with ratings
✅ Booking creation and management
✅ Notifications
✅ Reviews
✅ Job offers

### Frontend Pages Created
- `/services` - Browse services (updated)
- `/mechanics` - Browse mechanics (new)
- `/bookings` - Manage bookings (new, requires auth)

### React Query Hooks
All data fetching uses React Query for:
- Automatic caching
- Loading/error states
- Real-time updates
- Optimistic mutations

## 📚 Documentation

See `INTEGRATION_GUIDE.md` for:
- Complete API endpoint list
- Hook usage examples
- Configuration options
- Testing procedures

## 💡 Common Tasks

### Check if backend is running
```bash
curl http://localhost:8000/api/v1/services/
```
Should return JSON array of services

### Test signup
```bash
curl -X POST http://localhost:8000/api/v1/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+923001234567",
    "email": "test@example.com",
    "password": "Test@123",
    "password_confirm": "Test@123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### Test login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+923001234567",
    "password": "Test@123"
  }'
```

## 🎯 Next Steps

1. **Test all features** - Go through the test checklist above
2. **Connect payment system** - Update bookings endpoint to require payment
3. **Add real-time updates** - Consider WebSocket for live notifications
4. **Mobile optimization** - Test responsive design on phones
5. **Deploy** - Follow deployment guide for production setup

## 📞 Support

For issues:
1. Check browser console for errors
2. Check backend logs for API errors
3. Review test_apis_simple.py for expected API responses
4. Check INTEGRATION_GUIDE.md for detailed documentation
