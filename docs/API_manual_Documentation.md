# Hotel Booking System – API Documentation

**Version:** 1.0.0

**Framework:** FastAPI

**Last Updated:** November 15, 2025

**Authentication:** JWT Bearer Token (Cookie-based or Header-based)

**Content Type:** `application/json` or `multipart/form-data` (for file uploads)

---

## Overview

The **Hotel Booking System** is a comprehensive backend application built with **FastAPI**. It provides role-based access for **Admin** and **User**, enabling secure operations such as:

- User authentication and profile management
- Room type and room management
- Booking creation, rescheduling, and cancellation
- Payment processing and refunds
- Ratings and reviews
- Content management for website
- Real-time chat support
- Analytics and reporting dashboards

---

## Roles & Permissions

| Role | Capabilities |
| --- | --- |
| **Admin** | Full system access - manage users, rooms, bookings, content, view analytics |
| **User** | Register, login, book rooms, view bookings, manage profile, rate stays |

---

## Authentication Endpoints

### 1️⃣ **Register New User**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/user/register` | ❌ No | Register a new user account |

**Request Body:**

```json
{
  "firstName": "John",
  "lastName": "Doe",
  "email": "john.doe@example.com",
  "phoneNo": "9876543210",
  "password": "John@123",
  "role": "user"
}
```

**Response:**

```json
{
  "message": "OTP sent to email for verification"
}
```

---

### 2️⃣ **Verify Email with OTP**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/user/verify_email` | ❌ No | Verify email using OTP sent during registration |

**Request Body (Form Data):**

```
otp: "123456"
```

**Response:**

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "phone_no": "9876543210",
  "role": "user"
}
```

---

### 3️⃣ **Login**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/user/login` | ❌ No | Authenticate user with email/phone and password |

**Request Body (Form Data):**

```
user_email_or_password: "john.doe@example.com"
password: "John@123"
```

**Response:**

Sets `access_token` and `refresh_token` as HTTP-only cookies

```json
{
  "message": "Login successful",
  "token_type": "bearer"
}
```

---

### 4️⃣ **Refresh Access Token**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/user/refresh` | ✅ Yes (Refresh Token) | Get new access token using refresh token |

**Response:**

```json
{
  "message": "Token refreshed successfully",
  "token_type": "bearer"
}
```

---

### 5️⃣ **Logout**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/user/logout` | ✅ Yes | Clear authentication cookies and logout |

**Response:**

```json
{
  "message": "Logged out successfully",
  "detail": "Authentication cookies have been cleared"
}
```

---

### 6️⃣ **Forget Password**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `PUT` | `/user/forget-password` | ✅ Yes | Change user password |

**Request Body:**

```json
{
  "email": "john.doe@example.com",
  "prevPassword": "John@123",
  "curPassword": "John@456"
}
```

**Response:**

```json
{
  "message": "Password changed successfully"
}
```

---

## User Management Endpoints

### 1️⃣ **Get Current User Info**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/user/me` | ✅ Yes | Get authenticated user's information |

**Response:**

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "phone_no": "9876543210",
  "role": "user"
}
```

---

### 2️⃣ **Get All Users**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/user/users` | ✅ Yes (Admin) | Fetch all registered users |

**Response:**

```json
[
  {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone_no": "9876543210",
    "role": "user"
  }
]
```

---

### 3️⃣ **Delete User**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `DELETE` | `/user/user/{user_id}` | ✅ Yes (Admin) | Delete user by ID |

**Response:**

```json
{
  "message": "User deleted successfully"
}
```

---

### 4️⃣ **Update User Profile**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `PUT` | `/user/profile/{user_id}` | ✅ Yes | Update user profile with address and image |

**Request Body (Form Data):**

```
DOB: "1990-01-15"
street: "123 Main St"
city: "Mumbai"
state: "Maharashtra"
country: "India"
pincode: "400001"
image: <file>
remove_image: false
```

**Response:**

```json
{
  "DOB": "1990-01-15",
  "address": {
    "street": "123 Main St",
    "city": "Mumbai",
    "state": "Maharashtra",
    "country": "India",
    "pincode": "400001"
  },
  "image_url": "/static/profile_images/abc123.jpg",
  "updated_at": "2025-11-15T10:30:00"
}
```

---

### 5️⃣ **Search Users**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/user/search?q=john&page=1&per_page=10` | ✅ Yes (Admin) | Search users with pagination |

---

### 6️⃣ **Filter Users**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/user/filter?role_id=1&created_from=2025-01-01` | ✅ Yes (Admin) | Filter users by role and date |

---

## Room Type Endpoints

### 1️⃣ **Add Room Type**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/roomtype/add` | ✅ Yes (Admin) | Create new room type with features and bed types |

**Request Body (Form Data):**

```
room_name: "Deluxe Suite"
room_size: 3
base_price_per_night: 5000
no_of_adult: 2
no_of_child: 2
feature_ids: "1,2,3"
bed_type_id_with_count: ["1:1", "2:1"]
images: <files>
```

**Response:**

```json
{
  "id": 1,
  "room_name": "Deluxe Suite",
  "room_size": 3,
  "base_price": 5000,
  "no_of_adult": 2,
  "no_of_child": 2,
  "images": ["url1.jpg", "url2.jpg"],
  "bed_types": [
    {"id": 1, "bed_type_name": "King", "num_of_beds": 1},
    {"id": 2, "bed_type_name": "Single", "num_of_beds": 1}
  ],
  "features": [
    {"id": 1, "feature_name": "WiFi"},
    {"id": 2, "feature_name": "TV"}
  ],
  "total_beds": 2
}
```

---

### 2️⃣ **Update Room Type**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `PUT` | `/roomtype/update/{room_type_id}` | ✅ Yes (Admin) | Update room type details |

---

### 3️⃣ **Delete Room Type**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `DELETE` | `/roomtype/delete/{room_type_id}` | ✅ Yes (Admin) | Delete room type |

---

### 4️⃣ **Get Room Type**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/roomtype/get/{room_type_id}` | ✅ Yes | Get single room type with details |

---

### 5️⃣ **List Room Types**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/roomtype/list?page=1&per_page=10` | ✅ Yes | List all room types with pagination |

---

### 6️⃣ **Search Room Types**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/roomtype/search?q=deluxe&page=1` | ✅ Yes | Search room types |

---

### 7️⃣ **Filter Room Types**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/roomtype/filter?min_base_price=3000&max_base_price=8000` | ✅ Yes | Filter room types by price, size, capacity |

---

## Room Endpoints

### 1️⃣ **Add Room**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/room/add` | ✅ Yes (Admin) | Add new room |

**Request Body (Form Data):**

```
room_type_id: 1
floor_id: 3
room_no: 101
```

**Response:**

```json
{
  "success": true,
  "room": {
    "id": 1,
    "roomTypeId": 1,
    "floorId": 3,
    "roomNo": 101,
    "status": "available",
    "createdAt": "2025-11-15T10:30:00"
  }
}
```

---

### 2️⃣ **Update Room**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/room/update` | ✅ Yes (Admin) | Update room details including status |

**Request Body (Form Data):**

```
room_id: 1
status: "maintenance"
```

---

### 3️⃣ **Delete Room**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `DELETE` | `/room/delete` | ✅ Yes (Admin) | Delete room |

---

### 4️⃣ **Get Room by ID**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/room/{room_id}` | ✅ Yes | Get specific room details |

---

### 5️⃣ **Get All Rooms**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/room/?skip=0&limit=100` | ✅ Yes | Get all rooms with pagination |

---

### 6️⃣ **Search Rooms**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/room/search?q=101&page=1` | ✅ Yes | Search rooms by room number |

---

### 7️⃣ **Filter Rooms**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/room/filter?status=available&room_no=101` | ✅ Yes (Admin) | Filter rooms by criteria |

---

### 8️⃣ **Advanced Room Filter**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/room/whole/filter` | ✅ Yes | Filter rooms by price, size, features, availability dates |

**Query Parameters:**

```
room_price: 5000
floor_no: 3
min_room_size: 2
max_room_size: 4
no_of_child: 2
no_of_adult: 2
room_type_name: "Deluxe"
feature_ids: [1,2]
bed_type_ids: [1]
check_in: "2025-12-01"
check_out: "2025-12-05"
```

---

## Booking Endpoints

### 1️⃣ **Create Booking**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/booking/add` | ✅ Yes | Create new room booking with addons |

**Request Body:**

```json
{
  "room_id": 1,
  "check_in": "2025-12-01",
  "check_out": "2025-12-05",
  "booking_status": "confirmed"
}
```

**Query Parameter:**

```
addon_list: ["1:2", "3:1"]  // Format: addon_id:quantity
```

**Response:**

```json
{
  "message": "Booking created successfully",
  "booking": {
    "id": 1,
    "user_id": 5,
    "room_id": 1,
    "total_amount": 25000,
    "check_in": "2025-12-01",
    "check_out": "2025-12-05",
    "booking_status": "confirmed"
  },
  "total_amount": 25000,
  "invoice_sent": true
}
```

---

### 2️⃣ **Cancel Booking**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/booking/cancel` | ✅ Yes | Cancel booking with refund calculation |

**Request Body (Form Data):**

```
booking_id: 1
reason: "Change of plans"
```

**Response:**

```json
{
  "booking": {...},
  "refund_status": "approved",
  "total_amount": 25000,
  "refund_amount": 20000,
  "message": "Refund of 20000 will be processed in 2 days."
}
```

**Refund Rules:**
- 7+ days before check-in: 100% refund
- 3-6 days before check-in: 50% refund
- Less than 3 days: 80% refund

---

### 3️⃣ **Reschedule Booking**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/booking/reschedule` | ✅ Yes | Reschedule booking to new dates |

**Request Body (Form Data):**

```
booking_id: 1
check_in: "2025-12-10"
check_out: "2025-12-15"
```

**Response:**

```json
{
  "message": "Booking rescheduled successfully",
  "booking": {...},
  "new_total_amount": 28000,
  "paid_amount": 25000,
  "payment_difference": 3000,
  "reschedule_id": 1
}
```

**Rescheduling Rules:**
- Must be at least 3 days before check-in
- Only confirmed bookings can be rescheduled
- Can only reschedule once
- 20% deduction if refund is applicable

---

### 4️⃣ **Check Room Availability**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/booking/checkAvailability` | ✅ Yes | Check available dates for a room |

**Request Body (Form Data):**

```
room_id: 1
```

---

### 5️⃣ **List Bookings**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/booking/list?page=1&per_page=10` | ✅ Yes | List all bookings with pagination |

---

### 6️⃣ **Search Bookings**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/booking/search?q=john&page=1` | ✅ Yes | Search bookings |

---

### 7️⃣ **Filter Bookings**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/booking/filter` | ✅ Yes | Filter bookings by multiple criteria |

**Query Parameters:**

```
user_id: 5
room_id: 1
booking_status: "confirmed"
payment_status: "paid"
check_in_from: "2025-12-01"
check_in_to: "2025-12-31"
min_total_amount: 10000
max_total_amount: 50000
page: 1
per_page: 10
```

---

## Features Endpoints

### 1️⃣ **Add Feature**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/feature/add` | ✅ Yes (Admin) | Add room feature with image |

**Request Body (Form Data):**

```
feature_name: "WiFi"
image: <file>
```

---

### 2️⃣ **Update Feature Image**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/feature/update/image` | ✅ Yes (Admin) | Update feature image |

---

### 3️⃣ **Delete Feature**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `DELETE` | `/feature/delete` | ✅ Yes (Admin) | Delete feature |

---

### 4️⃣ **Get Feature**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/feature/get?feature_id=1` | ✅ Yes | Get single feature |

---

### 5️⃣ **List Features**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/feature/list` | ✅ Yes | Get all features |

---

## Addons Endpoints

### 1️⃣ **Add Addon**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/addon/add` | ✅ Yes (Admin) | Add booking addon (e.g., breakfast, parking) |

**Request Body (Form Data):**

```
addon_name: "Breakfast Buffet"
base_price: 500
image: <file>
```

---

### 2️⃣ **Update Addon Details**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/addon/update/details` | ✅ Yes (Admin) | Update addon name and price |

---

### 3️⃣ **Update Addon Image**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/addon/update/image` | ✅ Yes (Admin) | Update addon image |

---

### 4️⃣ **Delete Addon**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `DELETE` | `/addon/delete` | ✅ Yes (Admin) | Delete addon |

---

### 5️⃣ **Get Addon**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/addon/get?addon_id=1` | ✅ Yes | Get single addon |

---

### 6️⃣ **Search Addons**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/addon/search?q=breakfast` | ✅ Yes | Search addons |

---

### 7️⃣ **Filter Addons**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/addon/filter?base_price_min=100&base_price_max=1000` | ✅ Yes | Filter addons by price |

---

## Bed Types Endpoints

### 1️⃣ **Add Bed Type**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/bedtype/add` | ✅ Yes (Admin) | Add bed type (Single, Double, King, Queen) |

**Request Body (Form Data):**

```
bed_type_name: "King Size"
```

---

### 2️⃣ **Delete Bed Type**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `DELETE` | `/bedtype/delete?bed_type_name=King Size` | ✅ Yes (Admin) | Delete bed type |

---

### 3️⃣ **Get Bed Type**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/bedtype/get?bed_type_id=1` | ✅ Yes | Get single bed type |

---

### 4️⃣ **List Bed Types**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/bedtype/list?page=1&per_page=10` | ✅ Yes | List all bed types |

---

## Floor Endpoints

### 1️⃣ **Add Floor**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/floor/add` | ✅ Yes (Admin) | Add floor |

**Request Body (Form Data):**

```
floor_no: 3
```

---

### 2️⃣ **Delete Floor**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `DELETE` | `/floor/delete?floor_no=3` | ✅ Yes (Admin) | Delete floor |

---

### 3️⃣ **Get Floor**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/floor/get?floor_id=1` | ✅ Yes | Get single floor |

---

### 4️⃣ **List Floors**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/floor/list` | ✅ Yes | Get all floors |

---

## Ratings & Reviews Endpoints

### 1️⃣ **Add Rating/Review**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/ratings_reviews/add?booking_id=1` | ✅ Yes | Add review after completed stay |

**Request Body:**

```json
{
  "rating": 5,
  "review": "Excellent stay! Highly recommended.",
  "cleanliness": 5,
  "service": 5,
  "location": 4
}
```

**Response:**

```json
{
  "id": 1,
  "booking_id": 1,
  "room_id": 1,
  "object_id": "mongo_document_id"
}
```

---

### 2️⃣ **Get Rating/Review**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/ratings_reviews/{id}` | ✅ Yes | Get review details |

---

### 3️⃣ **Delete Rating/Review**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `DELETE` | `/ratings_reviews/delete?id=1` | ✅ Yes | Delete review |

---

## Content Management Endpoints

### 1️⃣ **Update Terms & Conditions**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `PUT` | `/content_management/terms_conditions/update` | ✅ Yes (Admin) | Update T&C |

---

### 2️⃣ **Get Terms & Conditions**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/content_management/terms_conditions` | ✅ Yes | Get T&C |

---

### 3️⃣ **Ask About Terms**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/content_management/ask_terms?question=What is cancellation policy` | ✅ Yes | AI-powered T&C Q&A |

---

### 4️⃣ **Add Carousel Image**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/content_management/carousel/add` | ✅ Yes (Admin) | Add homepage carousel image |

**Request Body (Form Data):**

```
title: "Summer Special"
description: "50% off on all bookings"
order: 1
is_active: true
images: <files>
```

---

### 5️⃣ **Get All Carousels**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/content_management/carousel/` | ✅ Yes | Get all carousel images |

---

### 6️⃣ **Update Carousel**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `PATCH` | `/content_management/carousel/update/{carousel_id}` | ✅ Yes (Admin) | Update carousel |

---

### 7️⃣ **Delete Carousel**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `DELETE` | `/content_management/carousel/delete/{carousel_id}` | ✅ Yes (Admin) | Delete carousel |

---

### 8️⃣ **Management Team CRUD**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/content_management/management/add` | ✅ Yes (Admin) | Add team member |
| `GET` | `/content_management/management/` | ✅ Yes | Get all team members |
| `PATCH` | `/content_management/management/update/{member_id}` | ✅ Yes (Admin) | Update team member |
| `DELETE` | `/content_management/management/delete/{member_id}` | ✅ Yes (Admin) | Delete team member |

---

### 9️⃣ **Contact Details CRUD**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/content_management/contact/add` | ✅ Yes (Admin) | Add contact info |
| `GET` | `/content_management/contact/` | ✅ Yes | Get contact info |
| `PATCH` | `/content_management/contact/update/{contact_id}` | ✅ Yes (Admin) | Update contact |
| `DELETE` | `/content_management/contact/delete/{contact_id}` | ✅ Yes (Admin) | Delete contact |

---

### 🔟 **Founder Info CRUD**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/content_management/founder/add` | ✅ Yes (Admin) | Add founder info |
| `GET` | `/content_management/founder/` | ✅ Yes | Get founder info |
| `PATCH` | `/content_management/founder/update/{founder_id}` | ✅ Yes (Admin) | Update founder |
| `DELETE` | `/content_management/founder/delete/{founder_id}` | ✅ Yes (Admin) | Delete founder |

---

### 1️⃣1️⃣ **Website Content Management**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/content_management/content-management/` | ✅ Yes (Admin) | Create/Update website content |
| `GET` | `/content_management/content-management/` | ✅ Yes | Get website content |
| `DELETE` | `/content_management/content-management/` | ✅ Yes (Admin) | Delete content |

---

## Dashboard & Analytics Endpoints

### 1️⃣ **Analytics Overview**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/dashboard/analytics?date_from=2025-01-01&date_to=2025-12-31` | ✅ Yes (Admin) | Get booking analytics |

**Response:**

```json
{
  "bookings": [...],
  "unique_customers": [1, 2, 3],
  "cancelled_bookings": [...],
  "total_bookings": 150,
  "cancelled_bookings_count": 10,
  "unique_customers_count": 120
}
```

---

### 2️⃣ **Cancelled Bookings Analysis**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/dashboard/cancelled_booking_analysis` | ✅ Yes (Admin) | Visual chart of cancellations |

**Returns:** PNG chart file

---

### 3️⃣ **Refund Revenue Loss Analysis**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/dashboard/refund_revenue_loss_analysis` | ✅ Yes (Admin) | Revenue loss from refunds |

**Returns:** PNG chart file

---

### 4️⃣ **Room Type Analytics**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/dashboard/room_type` | ✅ Yes (Admin) | Room type performance dashboard |

**Returns:** PNG dashboard with multiple charts

---

### 5️⃣ **User Analytics**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/dashboard/user` | ✅ Yes (Admin) | User conversion and behavior analytics |

**Returns:** PNG visualization file

---

## General Contact Endpoints

### 1️⃣ **Submit Contact Query**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/General/Query/create` | ❌ No | Submit general inquiry from public users |

**Request Body:**

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "subject": "Booking Question",
  "message": "I need help with my booking"
}
```

---

### 2️⃣ **Respond to Query**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `PUT` | `/General/Query/response` | ✅ Yes (Admin) | Admin responds to user query |

**Request Body:**

```json
{
  "query_id": "mongo_object_id",
  "response": "Thank you for your inquiry. Here's how we can help..."
}
```

---

### 3️⃣ **Get All Queries**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/General/Query/get` | ✅ Yes (Admin) | Get all contact queries |

---

## Chat Support Endpoints

### 1️⃣ **Get User Chat History**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/booked/contact/history/{user_id}` | ✅ Yes (Admin) | Get chat history for specific user |

---

### 2️⃣ **Delete User Chat**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `DELETE` | `/booked/contact/history/{user_id}` | ✅ Yes (Admin) | Delete user's chat history |

---

### 3️⃣ **Get All Users**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/booked/contact/user/all` | ✅ Yes (Admin) | Get all chat users with online status |

---

### 4️⃣ **Get Conversation Participants**

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/booked/contact/participants` | ✅ Yes (Admin) | Get all conversation participants |

---

## Backup & Restore Endpoints

### MongoDB Backup

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/mongo/backup-restore/backup` | ✅ Yes (Admin) | Create MongoDB backup |
| `GET` | `/mongo/backup-restore/backup/list` | ✅ Yes (Admin) | List available backups |
| `POST` | `/mongo/backup-restore/restore` | ✅ Yes (Admin) | Restore from backup file |
| `DELETE` | `/mongo/backup-restore/backup/{filename}` | ✅ Yes (Admin) | Delete backup file |

---

### PostgreSQL Backup

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/postgress/backup-restore/backup` | ✅ Yes (Admin) | Create PostgreSQL backup |
| `GET` | `/postgress/backup-restore/backup/download/{filename}` | ✅ Yes (Admin) | Download backup file |
| `POST` | `/postgress/backup-restore/restore` | ✅ Yes (Admin) | Restore database |

---

## Error Handling

| Status Code | Meaning | Description |
| --- | --- | --- |
| `200` | OK | Request successful |
| `201` | Created | Resource created successfully |
| `400` | Bad Request | Invalid input or validation failed |
| `401` | Unauthorized | Token missing, invalid, or expired |
| `403` | Forbidden | User lacks required permissions |
| `404` | Not Found | Resource not found |
| `409` | Conflict | Resource already exists |
| `422` | Unprocessable Entity | Validation error |
| `500` | Internal Server Error | Unexpected backend error |

---

## Common Response Formats

### Success Response

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": { ... }
}
```

### Error Response

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Paginated Response

```json
{
  "data": [...],
  "meta": {
    "page": 1,
    "per_page": 10,
    "total_items": 100,
    "total_pages": 10,
    "has_next": true,
    "has_prev": false
  }
}
```

---

## Token Lifecycle

| Type | Validity | Purpose | Storage |
| --- | --- | --- | --- |
| **Access Token** | 30 minutes | Used for every protected API call | HTTP-only cookie or Authorization header |
| **Refresh Token** | 7 days | Used to renew access token | HTTP-only cookie |
| **Revoked Token** | — | Invalidated immediately upon logout | Blacklist in Redis/DB |

---

## Authentication Flow

### Registration Flow

1. User submits registration data → `/user/register`
2. System sends OTP to email
3. User verifies email with OTP → `/user/verify_email`
4. Account created and activated

### Login Flow

1. User logs in with email/phone and password → `/user/login`
2. System validates credentials
3. Access token and refresh token set as HTTP-only cookies
4. User can access protected routes

### Token Refresh Flow

1. Access token expires (30 min)
2. Frontend automatically calls `/user/refresh`
3. System validates refresh token from cookie
4. New access token issued and set in cookie
5. User continues without re-login

### Logout Flow

1. User calls `/user/logout`
2. Both access and refresh token cookies cleared
3. Tokens added to blacklist (if implemented)
4. User must login again to access protected routes

---

## Authorization Header Format

For API clients not using cookies:

```
Authorization: Bearer <access_token>
```

Example:

```bash
curl -X GET "https://api.yourhotel.com/api/v1/user/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

---

## Booking Business Rules

### Cancellation Policy

- **7+ days before check-in**: 100% refund
- **3-6 days before check-in**: 50% refund  
- **Less than 3 days before check-in**: 80% refund
- Refunds processed within 2 business days
- Bank processing takes 5-10 additional days

### Rescheduling Policy

- Must be requested at least 3 days before check-in
- Can only reschedule once per booking
- Only confirmed bookings can be rescheduled
- Subject to room availability for new dates
- 20% deduction applies if price difference results in refund

### Booking Restrictions

- Check-in date must be in the future
- Check-out date must be after check-in date
- Room must be available for selected dates
- Full payment required at booking time
- Reviews only allowed after completed stays

---

## Image Upload Specifications

### Profile Images

- **Max Size**: 5MB
- **Formats**: JPG, PNG, GIF
- **Storage**: `/static/profile_images/`

### Room Type Images

- **Max Size**: 2MB per image
- **Formats**: JPG, PNG
- **Multiple**: Yes (up to 10 per room type)
- **Storage**: `/static/room_type_images/`

### Feature Images

- **Max Size**: 2MB
- **Formats**: JPG, PNG
- **Storage**: `/static/feature_images/`

### Addon Images

- **Max Size**: 2MB
- **Formats**: JPG, PNG
- **Storage**: `/static/addon_images/`

### Content Management Images

- **Carousel**: Multiple images, 5MB each
- **Management Team**: Single image per member
- **Founder**: Single image
- **Logo**: PNG preferred, transparent background

---

## Rate Limiting

*To be implemented*

- **Anonymous users**: 100 requests/hour
- **Authenticated users**: 1000 requests/hour
- **Admin users**: 5000 requests/hour

## Notes for Frontend Integration

### Cookie-Based Authentication (Recommended)

```javascript
// Login example
const response = await fetch('/api/v1/user/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: new URLSearchParams({
    user_email_or_password: 'john@example.com',
    password: 'John@123'
  }),
  credentials: 'include' // Important: include cookies
});
```

### Header-Based Authentication (Alternative)

```javascript
// Store token in memory or secure storage
const token = 'your_access_token';

const response = await fetch('/api/v1/user/me', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

### Handling Token Expiry

```javascript
// Axios interceptor example
axios.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      // Try to refresh token
      await axios.post('/api/v1/user/refresh', {}, { 
        withCredentials: true 
      });
      // Retry original request
      return axios(error.config);
    }
    return Promise.reject(error);
  }
);
```

### File Upload Example

```javascript
const formData = new FormData();
formData.append('room_name', 'Deluxe Suite');
formData.append('base_price_per_night', '5000');
formData.append('images', file1);
formData.append('images', file2);

await fetch('/api/v1/roomtype/add', {
  method: 'POST',
  body: formData,
  credentials: 'include'
});
```

---

## Testing Endpoints

### Health Check

```bash
GET /health
```

**Response:**

```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-11-15T10:30:00Z"
}
```

---

## Support & Contact

- **Documentation**: `https://docs.zyra.com`
- **Support Email**: `support@zyra.com`
- **Status Page**: `https://status.zyra.com`

---

**End of API Documentation**