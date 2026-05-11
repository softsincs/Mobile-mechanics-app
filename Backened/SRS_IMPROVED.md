# Software Requirements Specification (SRS) - MobileMechanic Platform
## Enterprise Edition - Version 2.0

---

## 1. Introduction

### 1.1 Purpose
This comprehensive Software Requirements Specification (SRS) outlines functional, non-functional, security, and architectural requirements for **MobileMechanic**, a production-grade, mobile-first platform designed to revolutionize car maintenance and repair services in Pakistan. This document serves as the definitive blueprint for developers, architects, DevOps engineers, security teams, QA professionals, and stakeholders to align on system features, technical constraints, security posture, scalability requirements, and development priorities.

### 1.2 Scope
MobileMechanic is a **three-tier, microservices-ready platform** enabling:

**Customer Users:**
- Register and manage profiles with multi-vehicle details and preferences
- Browse, search, filter, and book car maintenance services with dynamic pricing
- Real-time mechanic tracking with GPS-enabled location services
- Secure payments through multiple channels (JazzCash, Easypaisa, Stripe, Apple Pay, Google Pay)
- Comprehensive service history, analytics, and digital warranties
- Advanced rating and review system with verified reviews
- Notifications (push, SMS, email) with preference management
- Booking cancellation, rescheduling, and support ticket creation

**Mechanic Users:**
- Advanced profile management with certifications, specialties, and ratings
- Availability scheduling with calendar-based time slot management
- Real-time job assignment with acceptance/rejection logic
- In-app navigation and SOS functionality
- Job completion workflow with photo/video evidence upload
- Revenue dashboard and earnings analytics
- Skill-based availability and service categorization

**Admin Users:**
- Comprehensive dashboard with real-time metrics and KPIs
- Advanced user, mechanic, and booking management with bulk operations
- Certification verification and tier management
- Dispute resolution with mediation workflow
- Advanced analytics, business intelligence, and reporting
- Content management for services, categories, and promotions
- System monitoring, logs analysis, and performance tracking
- Finance module for payouts and commission management

**Platform Features:**
- Native iOS/Android apps with cross-platform React Native/Flutter
- Progressive Web App (PWA) for web access
- RESTful API v1, v2, v3 with GraphQL option for complex queries
- Real-time features via WebSockets (Socket.IO)
- Machine learning-based mechanic recommendation engine
- Predictive maintenance analytics
- Multi-city support with geographic expansion framework

---

## 2. Overall Description

### 2.1 Product Perspective & Architecture

#### 2.1.1 System Overview
```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT LAYER                              │
│  iOS App │ Android App │ Web (React) │ Admin Dashboard      │
└──────────────────┬──────────────────────────────────────────┘
                   │ (HTTPS/WebSocket)
┌──────────────────▼──────────────────────────────────────────┐
│                    API GATEWAY LAYER                         │
│  Load Balancer │ API Gateway │ Rate Limiter │ Auth Middleware│
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│              MICROSERVICES LAYER (Backend)                   │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐          │
│ │ Auth Service │ │Booking Svc   │ │Payment Svc   │          │
│ └──────────────┘ └──────────────┘ └──────────────┘          │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐          │
│ │ Dispatch Svc │ │ Tracking Svc │ │Notification │          │
│ └──────────────┘ └──────────────┘ └──────────────┘          │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐          │
│ │ Rating Svc   │ │ User Profile │ │ Analytics    │          │
│ └──────────────┘ └──────────────┘ └──────────────┘          │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│            CACHING & SESSION LAYER                           │
│ Redis (Primary) │ Redis Cluster │ Memcached (Fallback)     │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│           DATA PERSISTENCE LAYER                             │
│ PostgreSQL │ TimescaleDB │ Elasticsearch │ MongoDB (Logs)    │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│          EXTERNAL INTEGRATIONS                               │
│ Google Maps │ JazzCash │ Easypaisa │ Stripe │ Twilio │ FCM  │
└─────────────────────────────────────────────────────────────┘
```

#### 2.1.2 Technology Stack (Enterprise Grade)

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Backend API | Django 4.2+ / DRF 3.14+ | Mature, batteries-included, security-focused |
| Alternative Backend | FastAPI + Uvicorn | For high-performance services |
| Frontend (Mobile) | React Native / Flutter | Code reuse, native performance |
| Frontend (Web) | React 18+ / Next.js 13+ | SSR, SEO, optimized DX |
| Real-time | Socket.IO / Django Channels | WebSocket support, fallback mechanisms |
| Caching Layer | Redis 7.0+ (Cluster) | Session management, rate limiting, real-time data |
| Message Queue | Celery + RabbitMQ | Async tasks, email/SMS/push delivery |
| Primary Database | PostgreSQL 15+ | ACID compliance, advanced features (JSONB, GIS) |
| Time-Series DB | TimescaleDB | Location history, analytics aggregation |
| Search Engine | Elasticsearch 8.0+ | Full-text search, location filtering |
| File Storage | AWS S3 / MinIO | Scalable media storage |
| Logging | ELK Stack / Grafana Loki | Centralized logging, debugging |
| Monitoring | Prometheus + Grafana | Metrics, alerting, dashboards |
| CI/CD | GitHub Actions / GitLab CI | Automated testing, deployment |
| Container | Docker + Kubernetes | Orchestration, scaling |
| CDN | Cloudflare / AWS CloudFront | Static assets, API edge caching |

#### 2.1.3 External Integration Interfaces

| Service | Purpose | Failover Strategy |
|---------|---------|-------------------|
| Google Maps API | Geolocation, routing, tracking | Fallback to OpenStreetMap |
| JazzCash PSP | Primary payment gateway | Queue for retry, Easypaisa backup |
| Easypaisa PSP | Secondary payment gateway | Queue for retry, cash-on-delivery |
| Stripe | International payments (future) | Webhook validation, retry queue |
| Twilio | SMS/OTP delivery | Amazon SNS backup |
| Firebase Cloud Messaging (FCM) | Push notifications | In-app notification fallback |
| AWS SES | Email delivery | SendGrid backup |
| Sentry | Error tracking | Local logging fallback |

---

## 3. Security & Authentication

### 3.1 Multi-Factor Authentication (MFA)

#### 3.1.1 Supported MFA Methods
- **OTP via SMS**: Primary method, 6-digit code, 5-minute validity
- **Time-based OTP (TOTP)**: Google Authenticator, Authy support (optional for power users)
- **Email OTP**: Backup method when phone unavailable
- **Biometric**: Fingerprint/Face ID on mobile apps (secondary layer)
- **Security Questions**: Account recovery backup

#### 3.1.2 MFA Workflow
```
User Login
    ↓
Username/Email + Password Validation
    ↓
Generate MFA Token → Store in Redis (5 min TTL)
    ↓
Send OTP (SMS/Email)
    ↓
User Enters OTP
    ↓
Validate OTP ← Redis Check
    ↓
Generate JWT Token + Refresh Token
    ↓
Update Login Audit Log
    ↓
Access Granted
```

#### 3.1.3 Session Management
- JWT tokens with 15-minute expiration for access token
- Refresh tokens with 7-day expiration (rotate on refresh)
- Redis-backed token blacklist for logout
- Device fingerprinting for suspicious activity detection
- Max 3 active sessions per user (configurable)

### 3.2 Data Encryption

- **At Rest**: AES-256 encryption for sensitive fields (SSN, payment details)
- **In Transit**: TLS 1.3, HSTS headers, Certificate pinning for mobile apps
- **Secrets Management**: HashiCorp Vault or AWS Secrets Manager
- **Database Encryption**: PostgreSQL pgcrypto extension or native encryption
- **Field-Level Encryption**: Sensitive PII encrypted in database

### 3.3 Authorization & RBAC

#### Roles & Permissions
```
ADMIN
├── Full system access
├── User/Mechanic management
├── Finance & payouts
└── System configuration

CUSTOMER
├── Browse services
├── Book services
├── Payment processing
├── View own bookings
└── Rate mechanics

MECHANIC
├── Accept/reject jobs
├── Update availability
├── View assigned jobs
├── Upload job photos
└── View earnings

SUPPORT_AGENT
├── View all bookings
├── Resolve disputes
├── Access customer data
└── Generate reports

FINANCE_OFFICER
├── View payouts
├── Commission management
├── Revenue reports
└── Payment verification
```

### 3.4 API Security

- **API Versioning**: `/api/v1/`, `/api/v2/`, `/api/v3/` paths for backward compatibility
- **Rate Limiting**: 
  - 1000 requests/hour per user (standard)
  - 100 requests/hour per IP (non-authenticated)
  - 10000 requests/hour for service-to-service calls
  - Redis-backed sliding window rate limiter
- **API Key Management**: Rotatable API keys for third-party integrations
- **CORS**: Strict origin validation
- **CSRF Protection**: Token-based for state-changing operations
- **Input Validation**: Comprehensive validation with Pydantic/Serializers
- **Output Sanitization**: XSS prevention, JSON encoding validation

---

## 4. Functional Requirements

### 4.1 Authentication & User Management

#### 4.1.1 Registration Flow
**FR-1.1**: Users can register via:
- Phone number + OTP verification (primary)
- Email + verification link
- Social login (Google, Facebook) [Phase 2]

**Acceptance Criteria**:
- OTP generated and sent within 2 seconds
- OTP expires after 5 minutes or 3 failed attempts
- User data validated (phone format, email format)
- Duplicate account prevention (Redis-backed check)
- Terms & conditions acceptance required

**Backend Implementation**:
```python
# Django models
class User(AbstractUser):
    phone = PhoneNumberField(unique=True)
    phone_verified = BooleanField(default=False)
    mfa_enabled = BooleanField(default=True)
    preferred_mfa = CharField(choices=[...])
    otp_secret = CharField(null=True)  # For TOTP
    last_login_ip = GenericIPAddressField(null=True)
    login_device_fingerprint = CharField(null=True)
    
class OTPToken(Model):
    user = ForeignKey(User)
    otp_code = CharField()
    otp_type = CharField(choices=['SMS', 'EMAIL'])
    created_at = DateTimeField(auto_now_add=True)
    expires_at = DateTimeField()
    attempts = IntegerField(default=0)
    is_verified = BooleanField(default=False)

# API Endpoint
POST /api/v3/auth/register/
{
    "phone": "+923001234567",
    "email": "user@example.com",
    "password": "SecurePass123!",
    "first_name": "Ali",
    "last_name": "Khan"
}

Response (201):
{
    "user_id": "uuid",
    "otp_id": "uuid",
    "message": "OTP sent to registered phone",
    "expires_in": 300
}
```

#### 4.1.2 Login Flow with MFA
**FR-1.2**: Multi-factor authentication for login:
- Credentials verification (email/phone + password)
- OTP generation and delivery
- OTP validation
- JWT token issuance
- Device fingerprinting and audit logging

**Backend Implementation**:
```python
# Django REST Framework views
class LoginView(APIView):
    def post(self, request):
        # Step 1: Validate credentials
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({...}, status=400)
        
        user = User.objects.get(phone=serializer.data['phone'])
        
        # Step 2: Generate OTP
        otp = OTPService.generate_otp()
        cache.set(f"otp:{user.id}", otp, timeout=300)
        
        # Step 3: Send OTP (async)
        send_otp_task.delay(user.phone, otp)
        
        # Step 4: Create temporary session
        temp_token = create_temporary_token(user)
        
        return Response({
            'temp_token': temp_token,
            'mfa_required': True,
            'expires_in': 300
        })

class VerifyMFAView(APIView):
    def post(self, request):
        # Step 1: Validate temp token
        user = validate_temporary_token(request.data['temp_token'])
        
        # Step 2: Verify OTP
        otp_stored = cache.get(f"otp:{user.id}")
        if request.data['otp'] != otp_stored:
            raise IncorrectOTPError()
        
        # Step 3: Device fingerprinting
        fingerprint = generate_device_fingerprint(request)
        user.login_device_fingerprint = fingerprint
        user.last_login_ip = get_client_ip(request)
        user.last_login = now()
        user.save()
        
        # Step 4: Issue JWT tokens
        tokens = {
            'access_token': create_access_token(user),
            'refresh_token': create_refresh_token(user),
            'user': UserSerializer(user).data
        }
        
        # Step 5: Audit logging
        AuditLog.objects.create(
            user=user,
            action='LOGIN',
            ip_address=get_client_ip(request),
            device_fingerprint=fingerprint
        )
        
        return Response(tokens)
```

#### 4.1.3 User Profile Management
**FR-1.3**: Complete profile setup and management:
- Personal information (name, email, phone, DOB)
- Address management (home, office, billing)
- Vehicle management (multiple vehicles with details)
- Emergency contacts
- Profile picture upload
- Notification preferences
- Language preferences (Urdu, English, other regional languages)

**Backend Implementation**:
```python
class UserProfile(Model):
    user = OneToOneField(User)
    bio = TextField(blank=True)
    profile_picture = ImageField(upload_to='profiles/')
    date_of_birth = DateField(null=True)
    gender = CharField(choices=['M', 'F', 'O'])
    language = CharField(default='en')
    timezone = CharField(default='Asia/Karachi')
    
class Address(Model):
    user = ForeignKey(User)
    address_type = CharField(choices=['HOME', 'OFFICE', 'BILLING'])
    street_address = CharField()
    city = CharField()
    postal_code = CharField()
    latitude = FloatField()
    longitude = FloatField()
    is_default = BooleanField(default=False)
    label = CharField(max_length=100)

class Vehicle(Model):
    user = ForeignKey(User)
    make = CharField()
    model = CharField()
    year = IntegerField()
    registration_number = CharField(unique=True)
    color = CharField()
    last_service_date = DateField(null=True)
    next_service_date = DateField(null=True)
    mileage = IntegerField(null=True)
    fuel_type = CharField(choices=['Petrol', 'Diesel', 'CNG', 'Electric', 'Hybrid'])
    is_active = BooleanField(default=True)
    
class NotificationPreferences(Model):
    user = OneToOneField(User)
    push_notifications = BooleanField(default=True)
    sms_notifications = BooleanField(default=True)
    email_notifications = BooleanField(default=True)
    booking_reminders = BooleanField(default=True)
    promo_notifications = BooleanField(default=False)
    sound_enabled = BooleanField(default=True)
    
# API Endpoints
GET /api/v3/users/profile/
PUT /api/v3/users/profile/
POST /api/v3/users/vehicles/
GET /api/v3/users/vehicles/
PUT /api/v3/users/vehicles/{id}/
DELETE /api/v3/users/vehicles/{id}/
GET /api/v3/users/addresses/
POST /api/v3/users/addresses/
```

### 4.2 Service Management & Booking

#### 4.2.1 Service Catalog
**FR-2.1**: Dynamic service catalog with:
- Service categories (Maintenance, Repair, Inspection, etc.)
- Service items with descriptions, estimated duration, base price
- Seasonal pricing and surge pricing
- Service availability by city
- Service-to-mechanic specialization mapping

**Backend Implementation**:
```python
class ServiceCategory(Model):
    name = CharField()
    description = TextField()
    icon_url = URLField()
    is_active = BooleanField(default=True)

class Service(Model):
    category = ForeignKey(ServiceCategory)
    name = CharField()
    description = TextField()
    estimated_duration = IntegerField()  # in minutes
    base_price = DecimalField()
    max_price = DecimalField()
    min_price = DecimalField()
    is_active = BooleanField(default=True)
    
class ServicePrice(Model):
    service = ForeignKey(Service)
    city = CharField()
    peak_multiplier = DecimalField(default=1.0)  # Surge pricing
    off_peak_multiplier = DecimalField(default=1.0)
    weekend_multiplier = DecimalField(default=1.0)
    valid_from = DateTimeField()
    valid_to = DateTimeField(null=True)
    
class MechanicServiceSpecialty(Model):
    mechanic = ForeignKey('Mechanic')
    service = ForeignKey(Service)
    proficiency_level = CharField(choices=['BEGINNER', 'INTERMEDIATE', 'EXPERT'])
    years_experience = IntegerField()
    
# API Endpoints
GET /api/v3/services/categories/
GET /api/v3/services/?category=maintenance&city=lahore
GET /api/v3/services/{id}/pricing/?city=lahore
```

#### 4.2.2 Booking Workflow
**FR-2.2**: Complete booking lifecycle:
- Service selection
- Vehicle selection or temporary vehicle info
- Location input (GPS or manual address)
- Preferred time slot selection
- Add-ons selection (if applicable)
- Coupon/promo code application
- Price calculation with taxes
- Booking confirmation
- Real-time booking status updates

**Booking States**:
```
PENDING_CONFIRMATION
    ↓
CONFIRMED (Payment pending or received)
    ↓
MECHANIC_ASSIGNED
    ↓
MECHANIC_ACCEPTED / MECHANIC_REJECTED
    ↓
IN_PROGRESS
    ↓
COMPLETED / CANCELLED / NO_SHOW
    ↓
RATED / UNRATED
```

**Backend Implementation**:
```python
class Booking(Model):
    id = UUIDField(primary_key=True)
    customer = ForeignKey(User)
    service = ForeignKey(Service)
    vehicle = ForeignKey(Vehicle)
    mechanic = ForeignKey('Mechanic', null=True)
    status = CharField(choices=[...])
    
    # Location Info
    service_location = PointField()  # GIS field for geospatial queries
    service_address = TextField()
    city = CharField()
    latitude = FloatField()
    longitude = FloatField()
    
    # Timing
    scheduled_date = DateField()
    scheduled_time = TimeField()
    estimated_duration = IntegerField()  # in minutes
    start_time = DateTimeField(null=True)
    end_time = DateTimeField(null=True)
    
    # Pricing
    base_price = DecimalField()
    surge_multiplier = DecimalField(default=1.0)
    discount_percentage = DecimalField(default=0)
    discount_amount = DecimalField(default=0)
    tax_amount = DecimalField()
    total_amount = DecimalField()
    paid_amount = DecimalField(default=0)
    payment_method = CharField(choices=['JAZZCASH', 'EASYPAISA', 'CARD', 'CASH', 'WALLET'])
    
    # Status Tracking
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    confirmed_at = DateTimeField(null=True)
    started_at = DateTimeField(null=True)
    completed_at = DateTimeField(null=True)
    
    # Additional
    notes = TextField(blank=True)
    cancellation_reason = CharField(null=True)
    cancelled_by = CharField(choices=['CUSTOMER', 'MECHANIC', 'SYSTEM'])
    cancellation_date = DateTimeField(null=True)
    
# Booking API Workflow
POST /api/v3/bookings/
{
    "service_id": "uuid",
    "vehicle_id": "uuid",
    "scheduled_date": "2024-05-10",
    "scheduled_time": "14:00",
    "service_location": {
        "latitude": 31.5204,
        "longitude": 74.3587,
        "address": "123 Street, Lahore"
    },
    "add_ons": ["inspection"],
    "coupon_code": "WELCOME20"
}

Response (201):
{
    "booking_id": "uuid",
    "status": "PENDING_CONFIRMATION",
    "estimated_price": {
        "base": 5000,
        "tax": 500,
        "discount": 1000,
        "total": 4500
    },
    "estimated_mechanic_arrival": "2024-05-10T14:15:00Z",
    "expires_in": 600
}

# Confirm Booking (includes payment)
POST /api/v3/bookings/{id}/confirm/
{
    "payment_method": "JAZZCASH",
    "confirm": true
}

# Real-time Status Updates via WebSocket
WebSocket /ws/v3/bookings/{id}/
Events:
- BOOKING_CONFIRMED
- MECHANIC_ASSIGNED
- MECHANIC_ARRIVED
- JOB_STARTED
- JOB_COMPLETED
- MECHANIC_CANCELLED
```

#### 4.2.3 Dynamic Pricing Engine
**FR-2.3**: Intelligent pricing based on:
- Base service price
- Surge pricing (time-based: peak/off-peak/night)
- Weekend surcharge
- Geographic location (city multiplier)
- Demand-based multiplier
- Mechanic experience level (premium mechanics)
- Seasonal adjustments
- Promotional discounts
- Loyalty discounts

**Backend Implementation**:
```python
class DynamicPricingEngine:
    def calculate_price(self, service, location, datetime, mechanic=None):
        base_price = service.base_price
        
        # 1. Time-based multiplier
        time_multiplier = self.get_time_multiplier(datetime)
        
        # 2. Location multiplier
        location_multiplier = self.get_location_multiplier(location)
        
        # 3. Demand multiplier (real-time)
        demand_multiplier = cache.get(f"demand:{location}") or 1.0
        
        # 4. Experience multiplier
        exp_multiplier = 1.0
        if mechanic and mechanic.proficiency == 'EXPERT':
            exp_multiplier = 1.15
        
        # Calculate subtotal
        subtotal = base_price * time_multiplier * location_multiplier * demand_multiplier * exp_multiplier
        
        # Apply discount
        discount = self.calculate_discount(service, subtotal)
        
        # Add tax
        tax = (subtotal - discount) * TAX_RATE
        
        return {
            'base_price': base_price,
            'subtotal': subtotal,
            'discount': discount,
            'tax': tax,
            'total': subtotal - discount + tax
        }
    
    def get_time_multiplier(self, booking_datetime):
        hour = booking_datetime.hour
        if 6 <= hour < 9 or 17 <= hour < 20:  # Peak hours
            return 1.5
        elif 22 <= hour or hour < 6:  # Night surcharge
            return 1.25
        else:
            return 1.0
    
    def update_demand_multiplier(self):
        # Celery task to update demand based on booking requests vs available mechanics
        task.delay()  # Runs every 15 minutes
```

#### 4.2.4 Cancellation & Rescheduling
**FR-2.4**: User-friendly cancellation and rescheduling:
- Cancel before mechanic acceptance (full refund)
- Cancel after mechanic accepted (50% refund after 1 hour)
- Cancel within 30 minutes of scheduled time (no refund)
- Automatic cancellation after 2 hours of no-show
- Rescheduling to different time slot (free, once per booking)
- Cancellation reason tracking for analytics

**Backend Implementation**:
```python
class BookingCancellation(Model):
    booking = OneToOneField(Booking)
    cancelled_by = CharField()
    reason = TextField()
    refund_amount = DecimalField()
    refund_status = CharField(choices=['PENDING', 'PROCESSED', 'FAILED'])
    created_at = DateTimeField(auto_now_add=True)

def cancel_booking(booking, reason, cancelled_by='CUSTOMER'):
    now = timezone.now()
    time_until_booking = (booking.scheduled_date - now.date()).total_seconds()
    
    if booking.status == 'MECHANIC_ASSIGNED' and time_until_booking < 1800:  # < 30 min
        refund_amount = 0
    elif booking.status == 'CONFIRMED':
        refund_amount = booking.paid_amount * 1.0  # Full refund
    elif booking.status == 'MECHANIC_ASSIGNED' and time_until_booking < 3600:  # < 1 hour
        refund_amount = booking.paid_amount * 0.5
    else:
        refund_amount = 0
    
    booking.status = 'CANCELLED'
    booking.cancelled_by = cancelled_by
    booking.save()
    
    # Queue refund processing
    process_refund.delay(booking.id, refund_amount)
```

### 4.3 Dispatch & Assignment System

#### 4.3.1 Intelligent Mechanic Assignment
**FR-3.1**: Automatic assignment using weighted algorithm:
- Proximity (distance to booking location) - 40% weight
- Availability (current workload, free time slots) - 25% weight
- Specialization match (service expertise) - 20% weight
- Rating (mechanic average rating) - 10% weight
- Performance history (acceptance rate, completion time) - 5% weight

**Algorithm Implementation**:
```python
class MechanicAssignmentEngine:
    WEIGHTS = {
        'proximity': 0.40,
        'availability': 0.25,
        'specialization': 0.20,
        'rating': 0.10,
        'performance': 0.05
    }
    
    def find_best_mechanic(self, booking):
        mechanics = self.get_available_mechanics(booking)
        
        scores = []
        for mechanic in mechanics:
            score = (
                self.calculate_proximity_score(mechanic, booking) * self.WEIGHTS['proximity'] +
                self.calculate_availability_score(mechanic) * self.WEIGHTS['availability'] +
                self.calculate_specialization_score(mechanic, booking.service) * self.WEIGHTS['specialization'] +
                self.calculate_rating_score(mechanic) * self.WEIGHTS['rating'] +
                self.calculate_performance_score(mechanic) * self.WEIGHTS['performance']
            )
            scores.append((mechanic, score))
        
        # Return top 3 mechanics for fallback
        return sorted(scores, key=lambda x: x[1], reverse=True)[:3]
    
    def calculate_proximity_score(self, mechanic, booking):
        distance = self.haversine_distance(
            mechanic.current_location,
            booking.service_location
        )
        max_distance = 30  # km
        return max(0, (max_distance - distance) / max_distance) * 100
    
    def get_available_mechanics(self, booking):
        # Redis-backed real-time availability
        available_ids = cache.get(f"available_mechanics:{booking.city}") or []
        return Mechanic.objects.filter(id__in=available_ids, is_active=True)
```

#### 4.3.2 Notification & Job Offer Flow
**FR-3.2**: Multi-channel notification and job acceptance:
- Push notification with job details (5-second delay)
- SMS backup if no response (15-second delay)
- Auto-reject if no response within 60 seconds
- Mechanic can accept/reject with optional reason
- Fallback to next-best mechanic if rejected

**Implementation**:
```python
class JobOffer(Model):
    booking = ForeignKey(Booking)
    mechanic = ForeignKey(Mechanic)
    offered_at = DateTimeField(auto_now_add=True)
    expires_at = DateTimeField()
    response_time = FloatField(null=True)
    status = CharField(choices=['PENDING', 'ACCEPTED', 'REJECTED', 'EXPIRED'])
    rejection_reason = CharField(null=True)
    
def assign_mechanic_to_booking(booking):
    # Get ranked mechanics
    ranked_mechanics = MechanicAssignmentEngine.find_best_mechanic(booking)
    
    for mechanic in ranked_mechanics:
        job_offer = JobOffer.objects.create(
            booking=booking,
            mechanic=mechanic,
            expires_at=now() + timedelta(seconds=60)
        )
        
        # Send notifications asynchronously
        send_job_offer.delay(job_offer.id, mechanic.id)
        
        # Set expiry task
        expire_job_offer.apply_async(
            args=[job_offer.id],
            countdown=60
        )
        
        return job_offer

@celery_app.task
def send_job_offer(job_offer_id, mechanic_id):
    job_offer = JobOffer.objects.get(id=job_offer_id)
    mechanic = Mechanic.objects.get(id=mechanic_id)
    
    # 1. Push notification (Firebase)
    send_push_notification(
        mechanic.fcm_token,
        title="New Job Offer!",
        body=f"Service: {job_offer.booking.service.name}",
        data={'job_offer_id': str(job_offer_id)}
    )
    
    # 2. SMS backup (after 15 seconds)
    send_sms_notification.apply_async(
        args=[mechanic.phone, f"New job: {job_offer.booking.service.name}"],
        countdown=15
    )

@celery_app.task
def expire_job_offer(job_offer_id):
    job_offer = JobOffer.objects.get(id=job_offer_id)
    if job_offer.status == 'PENDING':
        job_offer.status = 'EXPIRED'
        job_offer.save()
        
        # Try next mechanic
        assign_mechanic_to_booking(job_offer.booking)
```

### 4.4 Real-Time Tracking

#### 4.4.1 Live Location Tracking
**FR-4.1**: Real-time mechanic location updates:
- Mechanic starts sharing location when job accepted
- Updates sent every 5 seconds (configurable based on battery/network)
- Customer sees real-time map with ETA calculation
- Automatic push notification at arrival
- Last location preserved for disputes

**Backend Implementation** (WebSockets):
```python
# Django Channels consumer
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class BookingTrackingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.booking_id = self.scope['url_route']['kwargs']['booking_id']
        self.booking_group_name = f'booking_{self.booking_id}'
        self.user = self.scope['user']
        
        # Validate permissions
        booking = await self.get_booking()
        if not self.user_has_access(booking):
            await self.close()
            return
        
        await self.channel_layer.group_add(
            self.booking_group_name,
            self.channel_name
        )
        await self.accept()
        
        # Send last known location
        last_location = await self.get_last_location()
        if last_location:
            await self.send_json({
                'type': 'location_update',
                'data': last_location
            })
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.booking_group_name,
            self.channel_name
        )
    
    async def location_update(self, event):
        # Broadcast location to consumers
        await self.send_json({
            'type': 'location_update',
            'mechanic_id': event['mechanic_id'],
            'latitude': event['latitude'],
            'longitude': event['longitude'],
            'accuracy': event['accuracy'],
            'timestamp': event['timestamp'],
            'eta': event['eta']
        })
```

#### 4.4.2 Mechanic Location Publishing
```python
# Mobile App sends location updates
POST /api/v3/mechanics/me/location/
{
    "latitude": 31.5204,
    "longitude": 74.3587,
    "accuracy": 10,
    "booking_id": "uuid",
    "speed": 30  // km/h
}

# Backend stores in Redis with TTL and broadcasts
class LocationService:
    def update_mechanic_location(self, mechanic, latitude, longitude, booking_id):
        # Store in Redis (expires in 30 seconds)
        cache.set(
            f"mechanic_location:{mechanic.id}",
            {
                'latitude': latitude,
                'longitude': longitude,
                'booking_id': booking_id,
                'timestamp': now().isoformat()
            },
            timeout=30
        )
        
        # Store in TimescaleDB for history
        LocationHistory.objects.create(
            mechanic=mechanic,
            booking=booking_id,
            location=Point(longitude, latitude)
        )
        
        # Calculate ETA
        eta = self.calculate_eta(latitude, longitude, booking.location)
        
        # Broadcast via WebSocket
        async_to_sync(channel_layer.group_send)(
            f'booking_{booking_id}',
            {
                'type': 'location_update',
                'mechanic_id': mechanic.id,
                'latitude': latitude,
                'longitude': longitude,
                'eta': eta
            }
        )
```

### 4.5 Payment Processing

#### 4.5.1 Payment Gateway Integration
**FR-5.1**: Multi-channel payment support with fallback mechanism:
- JazzCash/Easypaisa (primary for Pakistan)
- Stripe (future international support)
- Cash on Delivery
- Wallet (in-app credits)
- Digital payment methods (Apple Pay, Google Pay)

**Payment Flow**:
```
Booking Confirmed
    ↓
Payment Request Created (Status: PENDING)
    ↓
User Selects Payment Method
    ↓
Redirect to Payment Gateway (if PSP)
    ↓
Payment Gateway Returns (Success/Failure)
    ↓
Webhook Received & Verified
    ↓
Payment Status Updated
    ↓
If Success: Confirm Booking → Dispatch Mechanic
If Failure: Retry / Alternative Payment
```

**Backend Implementation**:
```python
class Payment(Model):
    id = UUIDField(primary_key=True)
    booking = OneToOneField(Booking)
    amount = DecimalField()
    currency = CharField(default='PKR')
    payment_method = CharField(choices=['JAZZCASH', 'EASYPAISA', 'CARD', 'WALLET', 'CASH'])
    status = CharField(choices=['PENDING', 'PROCESSING', 'SUCCESS', 'FAILED', 'REFUNDED'])
    
    # Gateway Info
    gateway_transaction_id = CharField(null=True)
    gateway_response = JSONField(null=True)
    
    # Retry Logic
    retry_count = IntegerField(default=0)
    max_retries = IntegerField(default=3)
    
    created_at = DateTimeField(auto_now_add=True)
    completed_at = DateTimeField(null=True)

class PaymentProcessor:
    def process_payment(self, booking, payment_method):
        payment = Payment.objects.create(
            booking=booking,
            amount=booking.total_amount,
            payment_method=payment_method
        )
        
        if payment_method == 'CASH':
            # No pre-authorization needed
            payment.status = 'PENDING'
            payment.save()
        
        elif payment_method in ['JAZZCASH', 'EASYPAISA']:
            # Redirect to PSP
            gateway = get_payment_gateway(payment_method)
            transaction_ref = gateway.create_transaction(
                amount=booking.total_amount,
                phone=booking.customer.phone,
                order_id=str(booking.id)
            )
            payment.gateway_transaction_id = transaction_ref
            payment.status = 'PROCESSING'
            payment.save()
            
            return {
                'redirect_url': gateway.get_redirect_url(transaction_ref),
                'payment_id': payment.id
            }
        
        elif payment_method == 'WALLET':
            # Deduct from wallet
            if booking.customer.wallet_balance >= booking.total_amount:
                booking.customer.wallet_balance -= booking.total_amount
                booking.customer.save()
                
                payment.status = 'SUCCESS'
                payment.completed_at = now()
                payment.save()
            else:
                payment.status = 'FAILED'
                payment.save()
                raise InsufficientWalletBalanceError()
        
        return payment

# Webhook for PSP Callback
@csrf_exempt
def payment_webhook(request):
    gateway_name = request.GET.get('gateway')
    gateway = get_payment_gateway(gateway_name)
    
    # Verify webhook signature
    if not gateway.verify_signature(request):
        return JsonResponse({'status': 'SIGNATURE_VERIFICATION_FAILED'}, status=403)
    
    transaction_id = request.POST.get('transaction_id')
    transaction_status = request.POST.get('status')
    
    payment = Payment.objects.get(gateway_transaction_id=transaction_id)
    payment.gateway_response = request.POST.dict()
    
    if transaction_status == 'SUCCESS':
        payment.status = 'SUCCESS'
        payment.completed_at = now()
        
        # Confirm booking
        booking = payment.booking
        booking.status = 'CONFIRMED'
        booking.confirmed_at = now()
        booking.save()
        
        # Dispatch mechanic
        assign_mechanic_to_booking.delay(booking.id)
        
        # Send confirmation
        send_booking_confirmation.delay(booking.id)
    
    elif transaction_status == 'FAILED':
        payment.status = 'FAILED'
        payment.retry_count += 1
        
        if payment.retry_count < payment.max_retries:
            # Queue for retry
            retry_payment.apply_async(
                args=[payment.id],
                countdown=300  # Retry after 5 minutes
            )
    
    payment.save()
    return JsonResponse({'status': 'WEBHOOK_PROCESSED'})
```

#### 4.5.2 Invoice & Receipt Generation
**FR-5.2**: Automatic invoice generation with:
- Service details with itemized breakdown
- Tax calculation
- Discounts applied
- Payment method confirmation
- Digital receipt (PDF + email)
- QR code for sharing

**Implementation**:
```python
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

class InvoiceGenerator:
    def generate_invoice(self, booking, payment):
        invoice = Invoice.objects.create(
            booking=booking,
            payment=payment,
            invoice_number=self.generate_invoice_number(),
            invoice_date=now()
        )
        
        # Generate PDF
        filename = f"invoice_{invoice.invoice_number}.pdf"
        filepath = os.path.join('invoices', filename)
        
        c = canvas.Canvas(filepath, pagesize=letter)
        
        # Header
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 750, f"Invoice #{invoice.invoice_number}")
        
        # Customer Details
        c.setFont("Helvetica", 10)
        c.drawString(50, 720, f"Customer: {booking.customer.get_full_name()}")
        c.drawString(50, 705, f"Phone: {booking.customer.phone}")
        
        # Booking Details
        y = 680
        c.drawString(50, y, "Service Details:")
        y -= 20
        c.setFont("Helvetica", 9)
        c.drawString(70, y, f"Service: {booking.service.name}")
        y -= 15
        c.drawString(70, y, f"Date: {booking.scheduled_date}")
        y -= 15
        c.drawString(70, y, f"Mechanic: {booking.mechanic.get_full_name() if booking.mechanic else 'TBD'}")
        
        # Itemization
        y -= 30
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, "Item")
        c.drawString(300, y, "Amount")
        y -= 15
        c.setFont("Helvetica", 9)
        c.line(50, y, 550, y)
        
        # Items
        y -= 15
        c.drawString(50, y, booking.service.name)
        c.drawString(300, y, f"PKR {booking.base_price}")
        
        # Discount
        if booking.discount_amount > 0:
            y -= 15
            c.drawString(50, y, "Discount")
            c.drawString(300, y, f"- PKR {booking.discount_amount}")
        
        # Tax
        y -= 15
        c.drawString(50, y, "Tax (17%)")
        c.drawString(300, y, f"+ PKR {booking.tax_amount}")
        
        # Total
        y -= 20
        c.setFont("Helvetica-Bold", 10)
        c.line(50, y, 550, y)
        y -= 15
        c.drawString(50, y, "Total Amount")
        c.drawString(300, y, f"PKR {booking.total_amount}")
        
        # Payment Method
        y -= 30
        c.setFont("Helvetica", 9)
        c.drawString(50, y, f"Payment Method: {payment.get_payment_method_display()}")
        
        # QR Code (for digital verification)
        y -= 30
        qr_code = self.generate_qr_code(invoice)
        c.drawImage(qr_code, 450, y - 60, width=60, height=60)
        
        c.save()
        
        # Send via email
        send_invoice_email.delay(booking.customer.email, filepath)
        
        return invoice
```

### 4.6 Rating & Review System

#### 4.6.1 Post-Service Rating
**FR-6.1**: Comprehensive feedback collection:
- Star rating (1-5) for mechanic
- Star rating for service quality
- Optional text review
- Photo evidence capability
- Report mechanism for fraudulent reviews

**Backend Implementation**:
```python
class Rating(Model):
    booking = OneToOneField(Booking)
    customer = ForeignKey(User)
    mechanic = ForeignKey(Mechanic)
    
    mechanic_rating = IntegerField(choices=range(1, 6))
    service_quality_rating = IntegerField(choices=range(1, 6))
    cleanliness_rating = IntegerField(choices=range(1, 6))
    
    review_text = TextField(blank=True)
    review_verified = BooleanField(default=False)  # Human moderation
    
    pros = JSONField(default=list)  # ['professional', 'on-time', etc]
    cons = JSONField(default=list)
    
    photos = JSONField(default=list)  # URLs of uploaded photos
    
    is_public = BooleanField(default=True)
    is_reported = BooleanField(default=False)
    report_reason = CharField(null=True)
    
    created_at = DateTimeField(auto_now_add=True)

class MechanicRatingAggregation(Model):
    mechanic = OneToOneField(Mechanic)
    total_ratings = IntegerField(default=0)
    average_rating = DecimalField(max_digits=3, decimal_places=2)
    rating_5_count = IntegerField(default=0)
    rating_4_count = IntegerField(default=0)
    rating_3_count = IntegerField(default=0)
    rating_2_count = IntegerField(default=0)
    rating_1_count = IntegerField(default=0)
    
    last_updated = DateTimeField(auto_now=True)

# Rating API
POST /api/v3/bookings/{id}/ratings/
{
    "mechanic_rating": 5,
    "service_quality_rating": 4,
    "cleanliness_rating": 5,
    "review_text": "Great service, very professional!",
    "pros": ["professional", "punctual"],
    "cons": []
}

# Celery task to update aggregation
@celery_app.task
def update_mechanic_rating_aggregation(mechanic_id):
    ratings = Rating.objects.filter(mechanic_id=mechanic_id, is_public=True)
    avg_rating = ratings.aggregate(Avg('mechanic_rating'))['mechanic_rating__avg']
    
    aggregation, created = MechanicRatingAggregation.objects.get_or_create(
        mechanic_id=mechanic_id
    )
    aggregation.total_ratings = ratings.count()
    aggregation.average_rating = avg_rating
    aggregation.rating_5_count = ratings.filter(mechanic_rating=5).count()
    # ... update other counts
    aggregation.save()
```

#### 4.6.2 Review Moderation
**FR-6.2**: Anti-fraud and quality assurance:
- AI-powered suspicious review detection
- Manual moderation by admins
- Flag for inappropriate content
- Report mechanism for users
- Reviewer credibility scoring

### 4.7 Notification System

#### 4.7.1 Multi-Channel Notifications
**FR-7.1**: Notifications via multiple channels:
- **Push Notifications**: Firebase Cloud Messaging (FCM)
- **SMS**: Twilio with local provider (Jazz, Zong)
- **Email**: AWS SES with HTML templates
- **In-App**: Real-time notifications in app
- **WhatsApp**: WhatsApp Business API (future)

**Architecture**:
```python
class Notification(Model):
    id = UUIDField(primary_key=True)
    recipient = ForeignKey(User)
    title = CharField()
    body = TextField()
    notification_type = CharField()  # BOOKING_CONFIRMED, MECHANIC_ARRIVED, etc.
    
    channels = JSONField(default=list)  # ['PUSH', 'SMS', 'EMAIL']
    is_sent = BooleanField(default=False)
    is_read = BooleanField(default=False)
    
    send_at = DateTimeField(default=now)
    sent_at = DateTimeField(null=True)
    read_at = DateTimeField(null=True)
    
    data = JSONField(default=dict)  # Additional context
    action_url = URLField(null=True)

class NotificationLog(Model):
    notification = ForeignKey(Notification)
    channel = CharField()  # PUSH, SMS, EMAIL
    status = CharField()  # SUCCESS, FAILED, RETRY
    provider_response = JSONField(null=True)
    created_at = DateTimeField(auto_now_add=True)

class NotificationService:
    def send_notification(self, notification_id):
        notification = Notification.objects.get(id=notification_id)
        
        for channel in notification.channels:
            try:
                if channel == 'PUSH':
                    self.send_push(notification)
                elif channel == 'SMS':
                    self.send_sms(notification)
                elif channel == 'EMAIL':
                    self.send_email(notification)
                elif channel == 'INAPP':
                    self.mark_for_inapp(notification)
                
                NotificationLog.objects.create(
                    notification=notification,
                    channel=channel,
                    status='SUCCESS'
                )
            except Exception as e:
                NotificationLog.objects.create(
                    notification=notification,
                    channel=channel,
                    status='FAILED',
                    provider_response=str(e)
                )
                # Queue retry
                retry_notification.apply_async(
                    args=[notification_id, channel],
                    countdown=300,
                    max_retries=3
                )
    
    def send_push(self, notification):
        fcm_token = notification.recipient.device_tokens.first()
        if not fcm_token:
            return
        
        message = messaging.Message(
            notification=messaging.Notification(
                title=notification.title,
                body=notification.body
            ),
            data=notification.data,
            android=messaging.AndroidConfig(
                priority='high'
            ),
            webpush=messaging.WebpushConfig(
                headers={'TTL': '3600'}
            ),
            token=fcm_token.token
        )
        
        response = messaging.send(message)
        return response
    
    def send_sms(self, notification):
        twilio_client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = twilio_client.messages.create(
            body=notification.body,
            from_=TWILIO_PHONE_NUMBER,
            to=notification.recipient.phone
        )
        return message.sid
    
    def send_email(self, notification):
        # Use Celery task for async email
        send_email_task.delay(
            recipient_email=notification.recipient.email,
            subject=notification.title,
            body=notification.body,
            notification_id=str(notification.id)
        )

# Celery task
@celery_app.task
def send_notification_async(notification_id):
    notification = Notification.objects.get(id=notification_id)
    service = NotificationService()
    service.send_notification(notification_id)
    notification.is_sent = True
    notification.sent_at = now()
    notification.save()

# Signal to send notification on booking confirmation
@receiver(post_save, sender=Booking)
def on_booking_confirmed(sender, instance, created, **kwargs):
    if instance.status == 'CONFIRMED':
        notification = Notification.objects.create(
            recipient=instance.customer,
            title="Booking Confirmed!",
            body=f"Your {instance.service.name} booking is confirmed.",
            notification_type='BOOKING_CONFIRMED',
            channels=['PUSH', 'SMS', 'EMAIL'],
            data={'booking_id': str(instance.id)}
        )
        send_notification_async.delay(notification.id)
```

#### 4.7.2 Notification Preferences
**FR-7.2**: User-controlled notification settings:
- Toggle by notification type
- Quiet hours (no notifications between X-Y)
- Channel preferences per notification type
- Frequency controls (daily digest option)
- Do Not Disturb mode

### 4.8 Mechanic Module

#### 4.8.1 Mechanic Registration & Verification
**FR-8.1**: Comprehensive onboarding process:
- Personal information collection
- Multi-document verification (CNIC, certifications, licenses)
- Background check integration (future)
- Service specialization selection
- Insurance verification
- Bank account setup for payouts

**Backend Implementation**:
```python
class Mechanic(Model):
    user = OneToOneField(User)
    verification_status = CharField(choices=['PENDING', 'VERIFIED', 'REJECTED', 'SUSPENDED'])
    verification_date = DateTimeField(null=True)
    verified_by = ForeignKey('User', null=True)
    
    # Profile
    years_experience = IntegerField()
    workshop_name = CharField(blank=True)
    workshop_address = TextField(blank=True)
    bio = TextField(blank=True)
    profile_picture = ImageField(upload_to='mechanics/')
    
    # Contact
    primary_phone = PhoneNumberField()
    emergency_contact = PhoneNumberField()
    
    # Specializations
    specialties = ManyToManyField(Service, through='MechanicServiceSpecialty')
    
    # Performance
    total_jobs_completed = IntegerField(default=0)
    current_rating = DecimalField(max_digits=3, decimal_places=2, default=0)
    acceptance_rate = DecimalField(max_digits=5, decimal_places=2, default=100)
    cancellation_rate = DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Availability
    is_active = BooleanField(default=False)
    current_location = PointField(null=True)  # GIS
    max_concurrent_jobs = IntegerField(default=3)
    
    # Banking
    bank_account_number = CharField(blank=True)
    bank_name = CharField(blank=True)
    account_title = CharField(blank=True)
    
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

class MechanicDocument(Model):
    mechanic = ForeignKey(Mechanic)
    document_type = CharField(choices=['CNIC', 'LICENSE', 'CERTIFICATION', 'INSURANCE'])
    document_file = FileField(upload_to='mechanic_docs/')
    is_verified = BooleanField(default=False)
    verified_at = DateTimeField(null=True)
    expiry_date = DateField(null=True)
    
    created_at = DateTimeField(auto_now_add=True)

# Mechanic Registration API
POST /api/v3/mechanics/register/
{
    "user": {
        "first_name": "Ahmed",
        "last_name": "Khan",
        "email": "ahmed@example.com",
        "phone": "+923001234567"
    },
    "mechanic": {
        "years_experience": 10,
        "specialties": ["oil_change", "brake_service"],
        "emergency_contact": "+923009876543"
    },
    "documents": [
        {"type": "CNIC", "file": "<base64>"},
        {"type": "LICENSE", "file": "<base64>"}
    ]
}
```

#### 4.8.2 Availability Management
**FR-8.2**: Flexible availability scheduling:
- Weekly schedule setup
- Break scheduling (lunch, prayer times)
- Geographic service area definition
- Vacation/temporary unavailability
- Real-time availability toggle
- Load balancing (prevent overwork)

**Implementation**:
```python
class MechanicAvailability(Model):
    mechanic = ForeignKey(Mechanic)
    day_of_week = IntegerField(choices=[(0, 'Monday'), ..., (6, 'Sunday')])
    start_time = TimeField()
    end_time = TimeField()
    is_available = BooleanField(default=True)
    
class MechanicBreak(Model):
    mechanic = ForeignKey(Mechanic)
    start_time = TimeField()
    end_time = TimeField()
    label = CharField()  # 'LUNCH', 'PRAYER', etc.
    
class MechanicVacation(Model):
    mechanic = ForeignKey(Mechanic)
    start_date = DateField()
    end_date = DateField()
    reason = CharField()
    
class MechanicServiceArea(Model):
    mechanic = ForeignKey(Mechanic)
    # Define service radius or specific areas
    center_location = PointField()  # Home/workshop location
    service_radius_km = IntegerField()  # Max service distance
    
class MechanicCurrentLoad(Model):
    """Real-time tracking of mechanic workload"""
    mechanic = ForeignKey(Mechanic)
    current_active_jobs = IntegerField(default=0)
    estimated_free_time = TimeField()
    is_available_for_new = BooleanField()
    last_updated = DateTimeField(auto_now=True)
```

#### 4.8.3 Job Management & Completion
**FR-8.3**: Complete job lifecycle for mechanics:
- Notification of new jobs with details
- Accept/reject with optional reason
- Start job with real-time tracking
- Add job notes and issues found
- Upload before/after photos
- Mark complete and get payment confirmation
- View job history with metrics

**Implementation**:
```python
class MechanicJob(Model):
    booking = OneToOneField(Booking)
    mechanic = ForeignKey(Mechanic)
    
    status = CharField(choices=['ASSIGNED', 'ACCEPTED', 'ARRIVED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED'])
    accepted_at = DateTimeField(null=True)
    started_at = DateTimeField(null=True)
    completed_at = DateTimeField(null=True)
    
    actual_duration = IntegerField(null=True)  # minutes
    
    issues_found = TextField(blank=True)
    job_notes = TextField(blank=True)
    before_photos = JSONField(default=list)
    after_photos = JSONField(default=list)
    
    parts_used = JSONField(default=list)  # [{"name": "oil filter", "cost": 500}]
    additional_charges = DecimalField(default=0)  # For unexpected issues
    
    signature_image = ImageField(null=True)  # Customer signature for job completion
    
    def start_job(self):
        self.status = 'IN_PROGRESS'
        self.started_at = now()
        self.save()
        
        # Notify customer
        send_notification_async.delay(
            Notification.objects.create(
                recipient=self.booking.customer,
                title="Mechanic Arrived",
                body=f"{self.mechanic.get_full_name()} has arrived to start your service."
            ).id
        )
    
    def complete_job(self, **kwargs):
        self.status = 'COMPLETED'
        self.completed_at = now()
        self.actual_duration = (now() - self.started_at).total_seconds() / 60
        
        if 'issues_found' in kwargs:
            self.issues_found = kwargs['issues_found']
        if 'notes' in kwargs:
            self.job_notes = kwargs['notes']
        
        self.save()
        
        # Notify customer
        send_notification_async.delay(
            Notification.objects.create(
                recipient=self.booking.customer,
                title="Service Completed",
                body=f"Your {self.booking.service.name} has been completed."
            ).id
        )
        
        # Generate invoice
        generate_invoice_task.delay(self.booking.id)
        
        # Update mechanic stats
        update_mechanic_stats.delay(self.mechanic.id)

# API Endpoints for Mechanic
GET /api/v3/mechanics/me/jobs/
GET /api/v3/mechanics/me/jobs/{id}/
PUT /api/v3/mechanics/me/jobs/{id}/accept/
PUT /api/v3/mechanics/me/jobs/{id}/start/
PUT /api/v3/mechanics/me/jobs/{id}/complete/
POST /api/v3/mechanics/me/jobs/{id}/upload-photos/
```

### 4.9 Admin Dashboard

#### 4.9.1 Dashboard Metrics & KPIs
**FR-9.1**: Real-time business analytics:
- Total bookings (today, week, month)
- Revenue metrics (total, average, growth)
- Active mechanics and customers
- Average rating and customer satisfaction
- Booking trends and peak hours
- Top services and mechanics
- Geographic heatmaps

**Implementation**:
```python
class DashboardMetrics(Model):
    date = DateField(unique=True)
    
    # Bookings
    total_bookings = IntegerField(default=0)
    completed_bookings = IntegerField(default=0)
    cancelled_bookings = IntegerField(default=0)
    
    # Revenue
    total_revenue = DecimalField(default=0)
    platform_commission = DecimalField(default=0)
    mechanic_payouts = DecimalField(default=0)
    
    # Users
    new_customers = IntegerField(default=0)
    new_mechanics = IntegerField(default=0)
    active_customers = IntegerField(default=0)
    active_mechanics = IntegerField(default=0)
    
    # Quality
    average_rating = DecimalField(max_digits=3, decimal_places=2)
    customer_satisfaction_score = DecimalField(max_digits=3, decimal_places=2)
    
    created_at = DateTimeField(auto_now_add=True)

# Celery task to aggregate metrics daily
@celery_app.task
def aggregate_daily_metrics():
    today = date.today()
    
    metrics = DashboardMetrics.objects.create(date=today)
    
    bookings_today = Booking.objects.filter(created_at__date=today)
    metrics.total_bookings = bookings_today.count()
    metrics.completed_bookings = bookings_today.filter(status='COMPLETED').count()
    metrics.cancelled_bookings = bookings_today.filter(status='CANCELLED').count()
    
    payments_today = Payment.objects.filter(created_at__date=today, status='SUCCESS')
    metrics.total_revenue = payments_today.aggregate(Sum('amount'))['amount__sum'] or 0
    
    ratings = Rating.objects.filter(created_at__date=today)
    if ratings.exists():
        metrics.average_rating = ratings.aggregate(Avg('mechanic_rating'))['mechanic_rating__avg']
    
    metrics.save()

# API Endpoints
GET /api/v3/admin/dashboard/metrics/
GET /api/v3/admin/dashboard/bookings/
GET /api/v3/admin/dashboard/revenue/
GET /api/v3/admin/dashboard/users/
```

#### 4.9.2 User & Mechanic Management
**FR-9.2**: Administrative user management:
- User search and filtering
- Mechanic verification and tier management
- Suspension/ban capabilities
- User communication (email/SMS)
- Bulk operations
- Dispute resolution interface

### 4.10 Analytics & Reporting

#### 4.10.1 Advanced Analytics
**FR-10.1**: Business intelligence and reporting:
- Booking analytics (by service, mechanic, location, time)
- Revenue reports (daily, weekly, monthly, yearly)
- Customer lifetime value (CLV) analysis
- Mechanic performance analytics
- Cohort analysis and retention rates
- Geographic performance heatmaps
- Prediction models for demand forecasting

**Implementation**:
```python
# Elasticsearch queries
class AnalyticsService:
    def __init__(self):
        self.es = Elasticsearch([ELASTICSEARCH_HOST])
    
    def get_booking_analytics(self, start_date, end_date, group_by='service'):
        query = {
            "range": {
                "created_at": {
                    "gte": start_date.isoformat(),
                    "lte": end_date.isoformat()
                }
            }
        }
        
        aggs = {
            "bookings_by_" + group_by: {
                "terms": {
                    "field": group_by,
                    "size": 100
                }
            }
        }
        
        result = self.es.search(
            index="bookings",
            body={"query": query, "aggs": aggs}
        )
        
        return result['aggregations']
    
    def get_revenue_analytics(self, start_date, end_date):
        query = {
            "bool": {
                "must": [
                    {"range": {"created_at": {"gte": start_date, "lte": end_date}}},
                    {"term": {"payment.status": "SUCCESS"}}
                ]
            }
        }
        
        aggs = {
            "total_revenue": {"sum": {"field": "payment.amount"}},
            "revenue_by_day": {
                "date_histogram": {
                    "field": "created_at",
                    "calendar_interval": "day"
                },
                "aggs": {
                    "daily_total": {"sum": {"field": "payment.amount"}}
                }
            }
        }
        
        return self.es.search(index="bookings", body={"query": query, "aggs": aggs})

# API Endpoints
GET /api/v3/admin/analytics/bookings/?group_by=service&start_date=2024-05-01&end_date=2024-05-31
GET /api/v3/admin/analytics/revenue/?period=monthly
GET /api/v3/admin/analytics/mechanics/?sort_by=performance
GET /api/v3/admin/analytics/customers/?metric=clv
```

---

## 5. Non-Functional Requirements

### 5.1 Performance Requirements

| Metric | Target | Details |
|--------|--------|---------|
| **API Response Time** | <500ms | P95 latency for all endpoints |
| **Booking Confirmation** | <2s | End-to-end from submission to confirmation |
| **Map Loading** | <3s | Real-time tracking map on 3G networks |
| **Mobile App Startup** | <5s | Cold start time |
| **Database Query** | <100ms | P95 for complex queries |
| **Search Response** | <200ms | Full-text search with filters |

### 5.2 Scalability & Capacity

- **Concurrent Users**: 50,000+ simultaneous active users
- **Bookings/Hour Peak**: 10,000+ bookings/hour (Eid, holidays)
- **API Requests/Second**: 100,000+ RPS
- **Database Connections**: 500+ pooled connections
- **Redis Connections**: 10,000+ concurrent connections
- **WebSocket Connections**: 50,000+ concurrent real-time connections
- **Geographic Coverage**: 50+ cities with automatic failover

### 5.3 Security Requirements

| Requirement | Implementation |
|-------------|-----------------|
| **Encryption** | TLS 1.3, AES-256 at-rest, field-level encryption for PII |
| **Authentication** | JWT + MFA (OTP, TOTP, Biometric) |
| **Data Protection** | GDPR/PDPA compliance, encryption keys in Vault |
| **API Security** | Rate limiting, CORS, CSRF tokens, API versioning |
| **Audit Logging** | All user actions logged, tamper-proof audit trail |
| **Compliance** | Pakistan PDPA, SOC 2 Type II, PCI DSS (for payments) |

### 5.4 Reliability & Availability

- **Uptime SLA**: 99.95% (excluding planned maintenance)
- **RTO (Recovery Time Objective)**: <15 minutes
- **RPO (Recovery Point Objective)**: <5 minutes
- **Backup Strategy**: Continuous replication + daily snapshots
- **Disaster Recovery**: Multi-region failover ready
- **Health Checks**: Every 30 seconds, auto-healing

### 5.5 Data Management

- **Retention Policy**: 
  - User data: Until account deletion + 90 days
  - Booking history: 7 years
  - Payment records: 7 years (compliance)
  - Logs: 30 days (hot), 1 year (cold storage)
- **GDPR Right to Be Forgotten**: 30-day deletion process
- **Data Minimization**: Collect only necessary data

---

## 6. Technical Stack (Detailed)

### 6.1 Backend Services Architecture

```
Mobile App/Web Client
    ↓ (HTTPS, JWT Auth)
API Gateway (Nginx/HAProxy)
    ├── Rate Limiter
    ├── Load Balancer
    └── Authentication Middleware
    
    ↓
Kubernetes Cluster
    ├── Auth Service (Django)
    ├── Booking Service (FastAPI)
    ├── Payment Service (Node.js)
    ├── Dispatch Service (FastAPI)
    ├── Tracking Service (Node.js + WebSocket)
    ├── Notification Service (Celery Worker)
    ├── Analytics Service (FastAPI + Elasticsearch)
    └── Admin Dashboard Backend (Django REST)

    ↓
Data Layer
    ├── PostgreSQL 15+ (Primary relational DB)
    ├── Redis 7.0+ Cluster (Cache, Sessions)
    ├── TimescaleDB (Time-series location data)
    ├── Elasticsearch 8.0+ (Search & Analytics)
    └── MongoDB (Logs, Unstructured data)

    ↓
Message Queue
    ├── RabbitMQ (Async tasks)
    └── Celery Workers (Email, SMS, Push, Reports)

    ↓
External Integrations
    ├── Google Maps API
    ├── Payment Gateways (JazzCash, Easypaisa)
    ├── SMS Provider (Twilio)
    ├── Email Service (AWS SES)
    ├── Push Notifications (FCM)
    └── Monitoring (Sentry, Datadog)
```

### 6.2 Technology Choices

```yaml
Backend Services:
  auth_service:
    language: Python
    framework: Django 4.2 + DRF 3.14
    purpose: Authentication, user management, MFA
    instances: 3+ (replicated)

  booking_service:
    language: Python
    framework: FastAPI
    purpose: Booking creation, management, state transitions
    instances: 5+ (high traffic)

  payment_service:
    language: Node.js/TypeScript
    framework: Express
    purpose: Payment processing, gateway integration
    instances: 3+ (replicated)

  dispatch_service:
    language: Python
    framework: FastAPI
    purpose: Intelligent mechanic assignment
    instances: 3+ (replicated)

  tracking_service:
    language: Node.js/TypeScript
    framework: Express + Socket.IO
    purpose: Real-time location tracking
    instances: 5+ (WebSocket intensive)

  notification_service:
    language: Python
    framework: Celery + Django Channels
    purpose: Multi-channel notifications (email, SMS, push)
    workers: 10+ (async tasks)

  analytics_service:
    language: Python
    framework: FastAPI + Elasticsearch Python client
    purpose: Aggregation, reporting, BI
    instances: 2+ (background)

Data:
  PostgreSQL:
    version: 15+
    pool_size: 500
    replication: Primary-Replica
    backups: Continuous + Daily snapshots
    
  Redis:
    version: 7.0+
    mode: Cluster (sharded)
    persistence: AOF + RDB
    replicas: 2+ per node
    
  Elasticsearch:
    version: 8.0+
    nodes: 5+ (distributed)
    shards: 3+ primary, 2+ replicas
    
  MongoDB:
    purpose: Logging, unstructured data
    replication: Replica set
    retention: 30 days hot, 1 year cold storage

Message Queue:
  RabbitMQ:
    purpose: Async task queue
    nodes: 3+ (cluster)
    
  Celery:
    workers: 10+
    tasks:
      - send_email
      - send_sms
      - send_push_notification
      - generate_invoice
      - process_refund
      - update_metrics
```

### 6.3 Infrastructure & DevOps

```yaml
Containerization:
  Docker:
    - Multi-stage builds for optimization
    - Images: One per service
    - Registry: Docker Hub / AWS ECR

Orchestration:
  Kubernetes:
    - 1 Master, 5+ Worker nodes
    - Helm charts for deployment
    - Istio for service mesh
    - Vertical Pod Autoscaler (VPA)
    - Horizontal Pod Autoscaler (HPA)

CI/CD:
  GitHub Actions / GitLab CI:
    - Automated testing on every PR
    - Docker image builds
    - Deployment to staging/production
    - Smoke tests post-deployment

Monitoring:
  Prometheus:
    - Metrics collection from all services
    - 2-week retention

  Grafana:
    - Dashboards for all key metrics
    - Custom alerts

  Sentry:
    - Error tracking
    - Performance monitoring
    - Release tracking

Logging:
  ELK Stack:
    - Elasticsearch: Log storage
    - Logstash: Log processing
    - Kibana: Log visualization
    - 30-day hot, 1-year cold storage

  Loki (alternative):
    - Lightweight log aggregation
    - Label-based queries

CDN:
  Cloudflare / AWS CloudFront:
    - Static assets caching
    - DDoS protection
    - Edge caching for APIs

Storage:
  AWS S3 / MinIO:
    - User uploads (photos, documents)
    - Backups
    - Versioning enabled
    - Encryption at rest

Secrets Management:
  HashiCorp Vault / AWS Secrets Manager:
    - Database credentials
    - API keys
    - JWS signing keys
    - Automatic rotation
```

---

## 7. Database Schema (Key Tables)

```sql
-- Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY,
    phone VARCHAR(20) UNIQUE,
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    user_type VARCHAR(20), -- CUSTOMER, MECHANIC, ADMIN
    mfa_enabled BOOLEAN DEFAULT true,
    mfa_method VARCHAR(20), -- OTP, TOTP, BIOMETRIC
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Bookings Table
CREATE TABLE bookings (
    id UUID PRIMARY KEY,
    customer_id UUID REFERENCES users(id),
    service_id UUID REFERENCES services(id),
    vehicle_id UUID REFERENCES vehicles(id),
    mechanic_id UUID REFERENCES users(id),
    status VARCHAR(50),
    service_location GEOMETRY(POINT),
    scheduled_date DATE,
    scheduled_time TIME,
    base_price DECIMAL(10,2),
    total_amount DECIMAL(10,2),
    payment_method VARCHAR(20),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    INDEX (customer_id),
    INDEX (status),
    INDEX (scheduled_date)
);

-- Payments Table
CREATE TABLE payments (
    id UUID PRIMARY KEY,
    booking_id UUID UNIQUE REFERENCES bookings(id),
    amount DECIMAL(10,2),
    payment_method VARCHAR(20),
    status VARCHAR(20),
    gateway_transaction_id VARCHAR(100),
    retry_count INT DEFAULT 0,
    created_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- Location History (TimescaleDB)
CREATE TABLE location_history (
    time TIMESTAMP,
    mechanic_id UUID,
    booking_id UUID,
    location GEOMETRY(POINT),
    accuracy FLOAT
) PARTITION BY TIME INTERVAL '1 day';

-- Notifications Table
CREATE TABLE notifications (
    id UUID PRIMARY KEY,
    recipient_id UUID REFERENCES users(id),
    title VARCHAR(200),
    body TEXT,
    channels JSONB, -- ['PUSH', 'SMS', 'EMAIL']
    is_read BOOLEAN DEFAULT false,
    created_at TIMESTAMP,
    read_at TIMESTAMP,
    INDEX (recipient_id, is_read)
);
```

---

## 8. API Versioning & Contract

### 8.1 API Endpoints Summary

**Auth Service**
```
POST   /api/v3/auth/register/              - User registration
POST   /api/v3/auth/login/                 - User login
POST   /api/v3/auth/verify-mfa/            - MFA verification
POST   /api/v3/auth/refresh-token/         - Refresh JWT token
POST   /api/v3/auth/logout/                - Logout
POST   /api/v3/auth/forgot-password/       - Password reset
POST   /api/v3/auth/verify-email/          - Email verification
```

**Booking Service**
```
GET    /api/v3/services/                   - List services
POST   /api/v3/bookings/                   - Create booking
GET    /api/v3/bookings/{id}/              - Get booking details
PUT    /api/v3/bookings/{id}/              - Update booking
DELETE /api/v3/bookings/{id}/              - Cancel booking
POST   /api/v3/bookings/{id}/confirm/      - Confirm booking
PUT    /api/v3/bookings/{id}/reschedule/   - Reschedule booking
GET    /api/v3/bookings/history/           - Booking history
```

**Mechanic Service**
```
POST   /api/v3/mechanics/register/         - Mechanic registration
GET    /api/v3/mechanics/me/               - Mechanic profile
PUT    /api/v3/mechanics/me/               - Update profile
POST   /api/v3/mechanics/me/availability/  - Set availability
GET    /api/v3/mechanics/me/jobs/          - Get assigned jobs
PUT    /api/v3/mechanics/me/jobs/{id}/     - Update job status
```

**Payment Service**
```
POST   /api/v3/payments/process/           - Process payment
GET    /api/v3/payments/{id}/              - Get payment status
POST   /api/v3/payments/{id}/refund/       - Process refund
```

**Rating Service**
```
POST   /api/v3/ratings/                    - Create rating
GET    /api/v3/ratings/?mechanic_id=...    - Get mechanic ratings
```

**Admin Service**
```
GET    /api/v3/admin/dashboard/            - Dashboard metrics
GET    /api/v3/admin/users/                - User management
GET    /api/v3/admin/mechanics/            - Mechanic management
GET    /api/v3/admin/analytics/            - Analytics & reporting
```

### 8.2 Error Handling & Status Codes

```python
# Standard Response Format
{
    "success": true/false,
    "data": {...},
    "error": {
        "code": "ERROR_CODE",
        "message": "Human-readable message",
        "details": {...}
    },
    "meta": {
        "timestamp": "ISO8601",
        "request_id": "uuid"
    }
}

# HTTP Status Codes
200 OK                  - Successful GET/PUT
201 Created            - Successful POST
400 Bad Request        - Validation error
401 Unauthorized       - Authentication failed
402 Payment Required   - Insufficient funds
403 Forbidden          - Authorization failed
404 Not Found          - Resource not found
409 Conflict           - State conflict (booking already confirmed)
429 Too Many Requests  - Rate limit exceeded
500 Internal Server Error - Server error
503 Service Unavailable - Maintenance / Service down
```

---

## 9. Security Implementation Details

### 9.1 JWT Token Structure

```
Header: {
    "alg": "HS256",
    "typ": "JWT"
}

Payload: {
    "sub": "user_uuid",
    "user_id": "uuid",
    "user_type": "CUSTOMER|MECHANIC|ADMIN",
    "phone": "+923001234567",
    "email": "user@example.com",
    "roles": ["user", "verified"],
    "device_fingerprint": "hash",
    "iat": 1672531200,
    "exp": 1672531200 + 900 (15 min),
    "iss": "MobileMechanic",
    "aud": "mobile_app"
}

Signature: HMAC-SHA256(base64UrlEncode(header) + "." + base64UrlEncode(payload), SECRET_KEY)
```

### 9.2 Rate Limiting Strategy

```python
# Redis-based sliding window rate limiter
class RateLimiter:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def is_allowed(self, identifier, limit=1000, window=3600):
        """
        Check if request is allowed within rate limit
        identifier: user_id or IP address
        limit: max requests per window
        window: time window in seconds
        """
        key = f"rate_limit:{identifier}"
        current = self.redis.incr(key)
        
        if current == 1:
            self.redis.expire(key, window)
        
        return current <= limit

# Usage in API middleware
def rate_limit_middleware(get_response):
    limiter = RateLimiter(redis_client)
    
    def middleware(request):
        user_identifier = request.user.id if request.user else get_client_ip(request)
        
        if not limiter.is_allowed(user_identifier):
            return JsonResponse(
                {"error": "Rate limit exceeded"},
                status=429
            )
        
        return get_response(request)
    
    return middleware
```

### 9.3 Field-Level Encryption

```python
# Encrypt sensitive fields in database
from django.db import models
from cryptography.fernet import Fernet

class EncryptedField(models.CharField):
    def __init__(self, *args, **kwargs):
        self.cipher = Fernet(settings.ENCRYPTION_KEY.encode())
        super().__init__(*args, **kwargs)
    
    def from_db_value(self, value, expression, connection):
        if value is None:
            return None
        return self.cipher.decrypt(value.encode()).decode()
    
    def get_prep_value(self, value):
        if value is None:
            return None
        return self.cipher.encrypt(value.encode()).decode()

# Usage
class User(Model):
    cnic = EncryptedField()  # National ID
    bank_account = EncryptedField()
```

---

## 10. Testing Strategy

### 10.1 Test Coverage Requirements

- **Unit Tests**: ≥80% code coverage
- **Integration Tests**: All critical workflows (booking, payment, dispatch)
- **E2E Tests**: Mobile app + web app user flows
- **Performance Tests**: Load testing with 50k concurrent users
- **Security Tests**: OWASP Top 10, penetration testing

### 10.2 Testing Tools

```yaml
Unit Testing:
  - Python: pytest + pytest-cov
  - JavaScript: Jest
  
Integration Testing:
  - Django: Django TestCase, Factory Boy
  - API: Postman/Newman

E2E Testing:
  - Mobile: Appium, Detox
  - Web: Cypress, Selenium

Load Testing:
  - Locust
  - JMeter
  - Artillery

Security Testing:
  - OWASP ZAP
  - Burp Suite Community
  - Bandit (Python linter)
```

---

## 11. Deployment & Release

### 11.1 Deployment Strategy

- **Blue-Green Deployment**: Zero-downtime releases
- **Canary Releases**: 5% → 25% → 50% → 100% traffic shift
- **Rollback Plan**: Automated rollback on health check failures

### 11.2 Release Checklist

```
Pre-Release:
☐ All tests passing
☐ Code review approved
☐ Security scan passed
☐ Database migrations tested
☐ Backup created
☐ Runbook prepared

Release:
☐ Deploy to staging
☐ Smoke tests passed
☐ Deploy to production (canary)
☐ Monitor metrics (5 min)
☐ Full production deployment
☐ Post-deployment verification

Post-Release:
☐ Monitor error rates
☐ Check performance metrics
☐ Customer communication
☐ Update runbook
```

---

## 12. Monitoring & Alerting

### 12.1 Key Metrics to Monitor

```yaml
Application Metrics:
  - API response time (P50, P95, P99)
  - Booking confirmation success rate
  - Payment success rate
  - Mechanic assignment success rate
  - User engagement (DAU, MAU)

Infrastructure Metrics:
  - CPU usage per service
  - Memory consumption
  - Disk I/O
  - Network bandwidth

Database Metrics:
  - Query response time
  - Connection pool utilization
  - Slow query log
  - Replication lag

Business Metrics:
  - Total bookings
  - Revenue
  - Customer satisfaction
  - Mechanic acceptance rate
```

### 12.2 Alert Thresholds

```
Critical:
- API response time > 2s for 5+ min
- Payment gateway down
- Database replication lag > 1 min
- Error rate > 5%

Warning:
- API response time > 1s for 5+ min
- Booking confirm success rate < 95%
- Mechanic assignment failure rate > 10%
- Queue processing lag > 5 min
```

---

## 13. Compliance & Legal

### 13.1 Data Protection

- **Pakistan Personal Data Protection Act (PDPA)**: User consent for data collection
- **GDPR Readiness**: Data export, deletion, and right to object
- **Payment Card Industry (PCI) DSS**: Secure payment processing
- **ISO 27001**: Information security management

### 13.2 Terms & Conditions

- User agreement with liability limits
- Dispute resolution mechanism
- Insurance coverage for services
- Cancellation policy
- Refund policy

---

## 14. Project Timeline & Phases

### Phase 1 (MVP) - 4-5 months
- Core user authentication with MFA
- Basic booking workflow
- Mechanic assignment and tracking
- Payment integration
- Basic ratings system
- Admin dashboard (basic)

### Phase 2 - 2-3 months
- Advanced analytics and reporting
- Subscription plans
- Emergency roadside assistance
- AI-based mechanic recommendations
- Promotion engine
- Customer support chatbot

### Phase 3 - 2-3 months
- Fleet management for corporate clients
- Predictive maintenance
- Mobile app offline capabilities
- WhatsApp integration
- International payment support
- Multi-language expansion

---

## 15. Resource Requirements

### 15.1 Team Composition

```
Backend Development:     4-5 engineers
Frontend Development:    3-4 engineers (iOS, Android, Web)
QA/Testing:             2-3 engineers
DevOps/Infrastructure:  2 engineers
Product Manager:        1
UX/UI Designer:         1-2
Security Engineer:      1 (consultant)
```

### 15.2 Infrastructure

- Kubernetes cluster (3 master + 5+ worker nodes)
- PostgreSQL managed service (AWS RDS)
- Redis cluster
- Elasticsearch cluster
- CDN service
- Monitoring stack (Prometheus, Grafana)

---

## 16. Success Metrics

| KPI | Target | Timeline |
|-----|--------|----------|
| User Downloads | 100K | 6 months |
| Active Users | 50K | 6 months |
| Monthly Bookings | 10K | 3 months |
| Revenue | PKR 50M+ | 12 months |
| Customer Satisfaction | 4.5/5 stars | Continuous |
| Mechanic Satisfaction | 4.5/5 stars | Continuous |
| System Uptime | 99.95% | Continuous |
| Payment Success Rate | 98%+ | Continuous |

---

## 17. Risk Assessment & Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Payment gateway integration delays | HIGH | Pre-integrate with multiple providers |
| Mechanic adoption challenges | HIGH | Competitive incentives, support team |
| Data security breach | CRITICAL | SOC 2 compliance, regular audits, insurance |
| Service quality issues | HIGH | Thorough vetting, ratings, penalties |
| Network connectivity in rural areas | MEDIUM | Offline mode, SMS fallback |
| Seasonal demand fluctuations | MEDIUM | Dynamic pricing, capacity planning |

---

## Document Information

- **Version**: 2.0 (Enterprise Edition)
- **Last Updated**: 2024-05-03
- **Status**: Final (Ready for Development)
- **Audience**: Developers, Architects, Product Managers, Stakeholders
- **Distribution**: Confidential - Internal Use Only

---

**End of SRS Document**