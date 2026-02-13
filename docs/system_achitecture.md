# System Architecture Document

**Hotel Booking System**

**Version:** 1.0.0

**Last Updated:** November 15, 2025

**Technology Stack:** FastAPI + PostgreSQL + MongoDB 

---

## Executive Summary

The Hotel Booking System is a comprehensive RESTful API-based application designed to manage hotel operations including room bookings, customer management, payment processing, and analytics. Built with FastAPI, PostgreSQL, and MongoDB, it provides secure, scalable endpoints for hotel management, booking operations, and customer service.

### Purpose

- Centralized hotel room and booking management
- Real-time room availability tracking
- Secure payment processing and refund management
- Role-based access for administrators and customers
- Content management for hotel website
- Analytics and reporting dashboards
- Real-time chat support for customers

### Key Features

- **User Management**: Registration with OTP verification, profile management
- **Room Management**: Room types, features, floors, bed types
- **Booking System**: Create, reschedule, cancel bookings with smart refund policies
- **Payment Processing**: Secure payment handling with refund management
- **Reviews & Ratings**: Customer feedback stored in MongoDB
- **Content Management**: Dynamic website content (carousels, team info, contact details)
- **Real-time Chat**: WebSocket-based customer support
- **Analytics Dashboard**: Booking trends, revenue analysis, user behavior
- **Backup & Restore**: Automated database backup for PostgreSQL and MongoDB

---

## High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         Client Layer                              │
│  (Web App, Mobile App, Admin Dashboard, Third-party Integrations)│
└───────────────────────────┬──────────────────────────────────────┘
                            │ HTTPS/REST & WebSocket
                            │
┌───────────────────────────▼──────────────────────────────────────┐
│                      FastAPI Application                          │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │              Authentication Middleware                      │  │
│  │         (JWT Token Validation & RBAC)                      │  │
│  │         (Cookie-based & Header-based Auth)                 │  │
│  └─────────────────────────┬──────────────────────────────────┘  │
│                            │                                      │
│  ┌─────────────────────────▼──────────────────────────────────┐  │
│  │                  API Router Layer                          │  │
│  │  • /user           • /roomtype        • /booking          │  │
│  │  • /room           • /addon           • /feature          │  │
│  │  • /floor          • /bedtype         • /dashboard        │  │
│  │  • /ratings_reviews • /content_management                 │  │
│  │  • /General/Query  • /booked/contact                      │  │
│  └─────────────────────────┬──────────────────────────────────┘  │
│                            │                                      │
│  ┌─────────────────────────▼──────────────────────────────────┐  │
│  │              Business Logic Layer                          │  │
│  │  • Room Availability Check  • Refund Calculation          │  │
│  │  • Price Calculation        • Rescheduling Rules          │  │
│  │  • OTP Generation           • Email Notifications         │  │
│  │  • PDF Invoice Generation   • Analytics Processing        │  │
│  └─────────────────────────┬──────────────────────────────────┘  │
│                            │                                      │
│  ┌─────────────────────────▼──────────────────────────────────┐  │
│  │            Data Access Layer (ORM)                         │  │
│  │         SQLAlchemy Models + MongoDB                        │  │
│  └─────────────────────────┬──────────────────────────────────┘  │
└────────────────────────────┼─────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                                         │
┌───────▼────────┐                        ┌───────▼────────┐  
│   PostgreSQL   │                        │    MongoDB     │ 
│  (Relational)  │                        │  (Documents)   │ 
│ • Bookings     │                        │ • Content Mgmt │ 
│ • Rooms        │                        │ • Chat History │ 
│ • Payments     │                        │ • Terms & Cond │ 
└────────────────┘                        └────────────────┘ 
        │                                         │                    │
        └────────────────────┴────────────────────┘
                             │
                ┌────────────▼────────────┐
                │   File Storage System   │
                │   (Static Files)        │
                │                         │
                │ • Profile Images        │
                │ • Room Images           │
                │ • Feature Icons         │
                │ • PDF Invoices          │
                │ • Backup Files          │
                └─────────────────────────┘
```

---

## 3. System Components
---

### FastAPI Application Layer

#### Authentication & Authorization Middleware

**Components**:
- **JWTBearer**: Custom authentication handler
  - Extracts tokens from cookies or headers
  - Validates token signature
  - Checks token expiration
  - Returns user object

- **Role-Based Access Control (RBAC)**:
  - `@require_scope()` decorator
  - Scope validation (user:read, room:write, etc.)
  - Permission enforcement

**Authentication Flow**:
```python
Request → Extract Token → Verify Signature → Check Expiry → 
Validate Scopes → Attach User to Request → Route Handler
```

#### API Router Layer

**Routers**:

| Router | Prefix | Purpose |
|--------|--------|---------|
| User | `/user` | Authentication, profile, user management |
| Room Type | `/roomtype` | Room type CRUD with features and bed types |
| Room | `/room` | Individual room management |
| Booking | `/booking` | Booking lifecycle management |
| Feature | `/feature` | Room features (WiFi, TV, etc.) |
| Addon | `/addon` | Booking addons (breakfast, parking) |
| Bed Type | `/bedtype` | Bed type management |
| Floor | `/floor` | Floor management |
| Ratings | `/ratings_reviews` | Customer reviews |
| Content Management | `/content_management` | Website content |
| Dashboard | `/dashboard` | Analytics and reports |
| General Query | `/General/Query` | Public contact queries |
| Chat | `/booked/contact` | Customer support chat |
| Backup (PostgreSQL) | `/postgress/backup-restore` | Database backup |
| Backup (MongoDB) | `/mongo/backup-restore` | MongoDB backup |

#### Business Logic Layer

**Core Services**:

1. **Authentication Service**
   - OTP generation and validation
   - Password hashing (bcrypt)
   - JWT token generation
   - Token refresh logic

2. **Booking Service**
   - Room availability checking
   - Price calculation (room + addons)
   - Booking validation
   - Cancellation with refund rules
   - Rescheduling with price adjustment

3. **Payment Service**
   - Payment processing
   - Refund calculation:
     - 7+ days: 100% refund
     - 3-6 days: 50% refund
     - <3 days: 80% refund
   - Transaction history

4. **Notification Service**
   - Email notifications (SMTP)
   - Booking confirmations
   - OTP emails
   - Invoice generation (PDF)

5. **Analytics Service**
   - Booking statistics
   - Revenue analysis
   - User behavior tracking
   - Chart generation (matplotlib, plotly)

6. **Search & Filter Service**
   - Room search with fuzzy matching
   - Multi-criteria filtering
   - Availability filtering by date range

7. **File Upload Service**
   - Image validation and storage
   - Thumbnail generation
   - File cleanup on deletion

#### Data Access Layer

**ORM**: SQLAlchemy

**Generic CRUD Operations**:
```python
- get_record(model, db, **filters)
- get_records(model, db)
- insert_record(model, db, **data)
- update_record(model, db, id, **data)
- delete_record(model, db, id)
- filter_record(model, db, **filters)
- search(model, db, q, page, per_page)
```

**MongoDB Operations**:
```python
- insert_record_mongo(collection, data)
- get_record_mongo(collection, id)
- delete_record_mongo(collection, id)
```

**Redis Operations**:
```python
- store_otp(email, otp, expiry)
- validate_otp(email, otp)
- cache_session(user_id, token)
```

---

## Database Architecture

### PostgreSQL (Relational Data)

#### Core Tables

**Users & Authentication**:
- `users`: User accounts (id, first_name, last_name, email, phone_no, role_id, password_hash, verified, created_at)
- `roles`: User roles (id, role_name: 'admin' | 'user')
- `user_profiles`: Extended user info (user_id, DOB, address, image_url)
- `otps`: Email verification OTPs (email, otp, temp_user_data, expiry)

**Room Management**:
- `room_type_with_sizes`: Room types (id, room_name, room_size, base_price, no_of_adult, no_of_child, images)
- `rooms`: Individual rooms (id, room_type_id, floor_id, room_no, status)
- `floors`: Building floors (id, floor_no)
- `bed_types`: Bed types (id, bed_type_name: 'Single', 'Double', 'King', 'Queen')
- `room_type_bed_types`: Many-to-many (room_type_id, bed_type_id, num_of_beds)
- `features`: Room features (id, feature_name, image)
- `room_type_features`: Many-to-many (room_type_id, feature_id)

**Booking & Payments**:
- `bookings`: Reservations (id, user_id, room_id, check_in, check_out, total_amount, booking_status)
- `payments`: Payment records (id, booking_id, total_amount, status)
- `refunds`: Refund records (id, payment_id, total_amount, refund_amount, status, reason)
- `reschedules`: Rescheduling history (id, booking_id, created_at)
- `addons`: Available addons (id, addon_name, base_price, image)
- `booking_addons`: Booking-addon link (booking_id, addon_id, quantity)

**Reviews & Ratings**:
- `ratings_reviews`: Review metadata (id, booking_id, room_id, object_id → MongoDB)

**Audit Trails**:
- `booking_status_history`: Status changes (booking_id, old_status, new_status, changed_at)
- `room_status_history`: Room status changes (room_id, old_status, new_status, changed_at)

#### Enums

```python
class BookingStatusEnum(str, Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class PaymentStatusEnum(str, Enum):
    PAID = "paid"
    REFUNDED = "refunded"
    PENDING = "pending"

class RefundStatusEnum(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING = "pending"

class RoomStatusEnum(str, Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    MAINTENANCE = "maintenance"
    RESERVED = "reserved"
```

#### Relationships

```
users ─┐
       ├──< bookings >── rooms ── room_type_with_sizes
       │                           ├──< room_type_bed_types >── bed_types
       │                           └──< room_type_features >── features
       └──< user_profiles

bookings ─┐
          ├──< payments ──< refunds
          ├──< booking_addons >── addons
          ├──< ratings_reviews (MongoDB link)
          └──< reschedules
```

---

### MongoDB (Document Store)

#### Collections

**Reviews Collection**:
```json
{
  "_id": ObjectId,
  "rating": 5,
  "review": "Excellent stay!",
  "cleanliness": 5,
  "service": 5,
  "location": 4,
  "created_at": ISODate
}
```

**Content Management Collection**:
```json
{
  "_id": ObjectId,
  "type": "carousel" | "management_team" | "contact" | "founder" | "terms_and_conditions",
  "data": {
    // Type-specific fields
  },
  "created_at": ISODate,
  "updated_at": ISODate
}
```

**Chat History Collection**:
```json
{
  "_id": ObjectId,
  "user_id": 5,
  "messages": [
    {
      "sender": "user" | "admin",
      "message": "Hello, I need help",
      "timestamp": ISODate
    }
  ],
  "status": "open" | "closed",
  "created_at": ISODate
}
```

**General Queries Collection**:
```json
{
  "_id": ObjectId,
  "name": "John Doe",
  "email": "john@example.com",
  "subject": "Booking Question",
  "message": "...",
  "response": "...",
  "status": "pending" | "responded",
  "created_at": ISODate
}
```

---

#### Directory Structure

```
app/static/
├── profile_images/          # User profile photos
├── room_type_images/        # Room type galleries
├── feature_images/          # Feature icons
├── addon_images/            # Addon images
├── carousel_images/         # Homepage carousel
├── management_team_images/  # Team photos
├── founder_images/          # Founder photo
└── content_logo/            # Website logo

app/backups/
├── postgressDB/            # PostgreSQL backups
└── mongoDB/                # MongoDB backups

app/invoices/               # Generated PDF invoices
```

#### File Management

**Upload Flow**:
1. Validate file type and size
2. Generate unique filename (UUID)
3. Save to appropriate directory
4. Store relative path in database
5. Return URL to client

**Deletion Flow**:
1. Fetch file path from database
2. Delete physical file
3. Remove database record

---


