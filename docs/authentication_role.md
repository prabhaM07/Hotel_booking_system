# Authentication & Role Documentation

**Project:** Hotel Booking System

**Version:** 1.0.0

**Last Updated:** November 15, 2025

---

## Overview

This document explains how **authentication** and **role-based access control (RBAC)** are implemented in the Hotel Booking System backend built with **FastAPI**.

It covers:
- Registration and email verification flow
- Login with cookie-based and header-based authentication
- JWT token management (access and refresh tokens)
- Role-based permissions for Admin and User roles
- Middleware and security implementation

---

## Authentication Flow

| Step | Description |
| --- | --- |
| **1. Register** | User registers with personal details (email, phone, password) |
| **2. Email Verification** | System sends OTP to email for verification |
| **3. Verify OTP** | User submits OTP to activate account |
| **4. Login** | System verifies credentials and issues Access + Refresh tokens |
| **5. Access Token** | Short-lived JWT (30 min) stored in HTTP-only cookie |
| **6. Refresh Token** | Long-lived JWT (7 days) stored in HTTP-only cookie |
| **7. Token Refresh** | Auto-refresh access token using refresh token |
| **8. Protected Routes** | Middleware verifies token and role before granting access |
| **9. Logout** | Clears both access and refresh token cookies |

---

## Architecture Diagram

```
┌─────────────┐
│   Client    │
│  (Browser)  │
└──────┬──────┘
       │
       │ 1. POST /user/register
       ▼
┌─────────────────────────────────┐
│   FastAPI Backend               │
│                                 │
│  ┌──────────────────────────┐  │
│  │  Registration Endpoint   │  │
│  │  - Validate input        │  │
│  │  - Generate OTP          │  │
│  │  - Store temp user data  │  │
│  │  - Send email with OTP   │  │
│  └──────────────────────────┘  │
└─────────────────────────────────┘
       │
       │ 2. Send OTP via Email
       ▼
┌─────────────┐
│ Email Service│
│  (SMTP)      │
└──────────────┘
       │
       │ 3. POST /user/verify_email
       ▼
┌─────────────────────────────────┐
│   Verification Endpoint         │
│  - Check OTP validity           │
│  - Check expiry                 │
│  - Create user account          │
│  - Delete OTP record            │
└─────────────────────────────────┘
       │
       │ 4. POST /user/login
       ▼
┌─────────────────────────────────┐
│   Login Endpoint                │
│  - Verify credentials           │
│  - Generate access token        │
│  - Generate refresh token       │
│  - Set HTTP-only cookies        │
└─────────────────────────────────┘
       │
       │ 5. Access Protected Routes
       ▼
┌─────────────────────────────────┐
│   JWT Middleware                │
│  - Extract token from cookie    │
│  - Verify token signature       │
│  - Check expiration             │
│  - Validate user permissions    │
│  - Attach user to request.state │
└─────────────────────────────────┘
```

---

## JWT Token Structure

### Access Token Example

```json
{
  "sub": "5",
  "email": "john.doe@example.com",
  "role": "user",
  "iat": 1700000000,
  "exp": 1700001800,
  "type": "access"
}
```

### Refresh Token Example

```json
{
  "sub": "5",
  "iat": 1700000000,
  "exp": 1700604800,
  "type": "refresh"
}
```

### Token Claims Explained

| Claim | Description | Example |
| --- | --- | --- |
| `sub` | Subject (User ID) | `"5"` |
| `email` | User's email address | `"john.doe@example.com"` |
| `role` | User's role | `"user"` or `"admin"` |
| `iat` | Issued At timestamp | `1700000000` |
| `exp` | Expiration timestamp | `1700001800` |
| `type` | Token type | `"access"` or `"refresh"` |

---

## Authentication Endpoints

### 1️⃣ Register New User

**Endpoint:** `POST /user/register`

**Auth Required:** ❌ No

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

**Validation Rules:**
- First name & last name: 1-50 alphabetic characters
- Email: Valid email format
- Phone: 10 digits starting with 6-9
- Password: Min 6 chars, 1 uppercase, 1 number, 1 special char
- Role: "user" (default) or "admin"

**Response:**

```json
{
  "message": "OTP sent to email for verification",
  "email": "john.doe@example.com"
}
```

**Process:**
1. Validates input data
2. Generates 6-digit OTP
3. Stores temporary user data with OTP in database
4. Sends OTP to user's email
5. OTP expires in 10 minutes

---

### 2️⃣ Verify Email with OTP

**Endpoint:** `POST /user/verify_email`

**Auth Required:** ❌ No

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

**Error Cases:**
- `404`: OTP not found
- `400`: Incorrect OTP
- `400`: OTP expired

**Process:**
1. Validates OTP exists
2. Checks OTP matches
3. Verifies OTP not expired
4. Creates permanent user account
5. Marks user as verified
6. Deletes OTP record

---

### 3️⃣ Login

**Endpoint:** `POST /user/login`

**Auth Required:** ❌ No

**Request Body (Form Data):**

```
user_email_or_password: "john.doe@example.com"  (or "9876543210")
password: "John@123"
```

**Response:**

```json
{
  "message": "Login successful",
  "token_type": "bearer",
  "user": {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "role": "user"
  }
}
```

**Cookies Set:**
- `access_token` (HTTP-only, 30 min expiry)
- `refresh_token` (HTTP-only, 7 days expiry)

**Process:**
1. Accepts email OR phone number as identifier
2. Verifies password using bcrypt
3. Generates access token (30 min)
4. Generates refresh token (7 days)
5. Sets both tokens as HTTP-only cookies
6. Returns user information

---

### 4️⃣ Refresh Access Token

**Endpoint:** `POST /user/refresh`

**Auth Required:** ✅ Yes (Refresh Token)

**Request:** Uses refresh token from cookie

**Response:**

```json
{
  "message": "Token refreshed successfully",
  "token_type": "bearer"
}
```

**Process:**
1. Extracts refresh token from cookie
2. Verifies refresh token signature
3. Checks token type is "refresh"
4. Generates new access token
5. Sets new access token cookie
6. Refresh token remains unchanged

---

### 5️⃣ Logout

**Endpoint:** `POST /user/logout`

**Auth Required:** ✅ Yes

**Response:**

```json
{
  "message": "Logged out successfully",
  "detail": "Authentication cookies have been cleared"
}
```

**Process:**
1. Clears `access_token` cookie
2. Clears `refresh_token` cookie
3. Optionally adds tokens to blacklist (if implemented)

---

### 6️⃣ Change Password

**Endpoint:** `PUT /user/forget-password`

**Auth Required:** ✅ Yes

**Request Body:**

```json
{
  "email": "john.doe@example.com",
  "prevPassword": "John@123",
  "curPassword": "John@456"
}
```

**Validation:**
- User can only change their own password
- Previous password must be correct
- New password must meet complexity requirements
- New password must differ from old password

---

## Role-Based Access Control (RBAC)

### Available Roles

| Role | Description | Access Level |
| --- | --- | --- |
| **user** | Regular customer | Can book rooms, manage profile, view own bookings |
| **admin** | System administrator | Full access to all resources and operations |

---

## Permission Scopes

The system uses scope-based permissions checked via `@require_scope()` decorator.

### User Scopes

| Scope | Description | Admin | User |
| --- | --- | --- | --- |
| `user:read` | View user information | ✅ | ✅ |
| `user:write` | Manage users | ✅ | ❌ |
| `user:update` | Update user profile | ✅ | ✅ (own only) |
| `user:delete` | Delete users | ✅ | ❌ |

### Room Management Scopes

| Scope | Description | Admin | User |
| --- | --- | --- | --- |
| `room:read` | View rooms | ✅ | ✅ |
| `room:write` | Create/edit rooms | ✅ | ❌ |
| `room:delete` | Delete rooms | ✅ | ❌ |

### Room Type Scopes

| Scope | Description | Admin | User |
| --- | --- | --- | --- |
| `roomtype:read` | View room types | ✅ | ✅ |
| `roomtype:write` | Create/edit room types | ✅ | ❌ |
| `roomtype:delete` | Delete room types | ✅ | ❌ |

### Booking Scopes

| Scope | Description | Admin | User |
| --- | --- | --- | --- |
| `booking:read` | View bookings | ✅ | ✅ (own only) |
| `booking:write` | Create bookings | ✅ | ✅ |
| `booking:update` | Update bookings | ✅ | ✅ (own only) |
| `booking:delete` | Cancel bookings | ✅ | ✅ (own only) |

### Feature/Addon/Floor/BedType Scopes

| Scope | Description | Admin | User |
| --- | --- | --- | --- |
| `feature:read` | View features | ✅ | ✅ |
| `feature:write` | Manage features | ✅ | ❌ |
| `feature:delete` | Delete features | ✅ | ❌ |
| `addon:read` | View addons | ✅ | ✅ |
| `addon:write` | Manage addons | ✅ | ❌ |
| `addon:delete` | Delete addons | ✅ | ❌ |
| `floor:read` | View floors | ✅ | ✅ |
| `floor:write` | Manage floors | ✅ | ❌ |
| `floor:delete` | Delete floors | ✅ | ❌ |
| `bedtype:read` | View bed types | ✅ | ✅ |
| `bedtype:write` | Manage bed types | ✅ | ❌ |
| `bedtype:delete` | Delete bed types | ✅ | ❌ |

### Content Management Scopes

| Scope | Description | Admin | User |
| --- | --- | --- | --- |
| `scope:read` | View content | ✅ | ✅ |
| `scope:write` | Manage content | ✅ | ❌ |
| `scope:delete` | Delete content | ✅ | ❌ |

---

## Middleware Implementation

### JWT Authentication Middleware

**File:** `app/auth/jwt_bearer.py`

```python
class JWTBearer(HTTPBearer):
    """
    Authenticates requests using JWT tokens from:
    1. HTTP-only cookies (preferred)
    2. Authorization header (fallback)
    """
    
    async def __call__(self, request: Request) -> str:
        # Extract token from cookie or header
        token = get_token(request)
        
        # Verify token signature and expiry
        payload = verify_access_token(token)
        
        # Extract and return user_id
        user_id = payload.get("sub")
        return user_id
```

**Token Extraction Priority:**
1. **Cookie**: `access_token` cookie (preferred for web apps)
2. **Header**: `Authorization: Bearer <token>` (for API clients)

---

### Authorization Middleware

**File:** `app/auth/auth_utils.py`

```python
def require_scope(required_scopes: List[str]):
    """
    Decorator to enforce scope-based permissions.
    
    Usage:
        @require_scope(["user:write"])
        async def create_user(...):
            ...
    """
    async def dependency(request: Request, db: Session):
        user_id = await jwt_bearer(request)
        user = get_user_from_db(db, user_id)
        
        # Attach user to request state
        request.state.user = user
        
        # Check if user has required scopes
        if not has_required_scopes(user, required_scopes):
            raise HTTPException(403, "Insufficient permissions")
        
        return user
    
    return Depends(dependency)
```

---

## Security Implementation

### Token Generation

**File:** `app/auth/jwt_handler.py`

```python
def create_access_token(data: Dict) -> str:
    """Generate access token (30 min expiry)"""
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=30)
    
    to_encode.update({
        "exp": expire,
        "type": "access"
    })
    
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

def create_refresh_token(data: Dict) -> str:
    """Generate refresh token (7 days expiry)"""
    to_encode = data.copy()
    expire = datetime.now() + timedelta(days=7)
    
    to_encode.update({
        "exp": expire,
        "type": "refresh"
    })
    
    return jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm="HS256")
```

---

### Token Verification

```python
def verify_access_token(token: str) -> Dict:
    """Verify access token signature and expiry"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        
        if payload.get("type") != "access":
            raise HTTPException(401, "Invalid token type")
        
        return payload
    
    except JWTError:
        raise HTTPException(401, "Could not validate credentials")

def verify_refresh_token(token: str) -> Dict:
    """Verify refresh token"""
    try:
        payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=["HS256"])
        
        if payload.get("type") != "refresh":
            raise HTTPException(401, "Invalid token type")
        
        return payload
    
    except JWTError:
        raise HTTPException(401, "Invalid refresh token")
```

---

### Password Hashing

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)
```

---

## Usage Examples

### Protected Endpoint Example

```python
@router.get("/booking/list")
@require_scope(["booking:read"])
async def list_bookings(
    request: Request,
    db: Session = Depends(get_db)
):
    """List user's bookings"""
    current_user = request.state.user
    
    if current_user.role == "admin":
        # Admin sees all bookings
        bookings = get_all_bookings(db)
    else:
        # User sees only their bookings
        bookings = get_user_bookings(db, current_user.id)
    
    return bookings
```

---

### Role Check Example

```python
@router.delete("/room/{room_id}")
@require_scope(["room:delete"])
async def delete_room(
    request: Request,
    room_id: int,
    db: Session = Depends(get_db)
):
    """Delete room - Admin only"""
    # Scope decorator already verified admin role
    delete_room_from_db(db, room_id)
    return {"message": "Room deleted"}
```

---

## Frontend Integration

### Cookie-Based Authentication (Recommended)

```javascript
// Login
async function login(email, password) {
  const formData = new URLSearchParams({
    user_email_or_password: email,
    password: password
  });
  
  const response = await fetch('/api/v1/user/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formData,
    credentials: 'include' // Include cookies
  });
  
  return response.json();
}

// Access protected route
async function getUserProfile() {
  const response = await fetch('/api/v1/user/me', {
    credentials: 'include' // Include cookies
  });
  
  return response.json();
}

// Logout
async function logout() {
  await fetch('/api/v1/user/logout', {
    method: 'POST',
    credentials: 'include'
  });
  
  // Redirect to login page
  window.location.href = '/login';
}
```

---

### Automatic Token Refresh

```javascript
// Axios interceptor for auto-refresh
axios.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Try to refresh token
        await axios.post('/api/v1/user/refresh', {}, {
          withCredentials: true
        });
        
        // Retry original request
        return axios(originalRequest);
      } catch (refreshError) {
        // Refresh failed, redirect to login
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);
```

---

### Header-Based Authentication (Alternative)

```javascript
// Store token in memory (not localStorage for security)
let accessToken = null;

async function login(email, password) {
  const response = await fetch('/api/v1/user/login', {
    method: 'POST',
    body: formData
  });
  
  const data = await response.json();
  accessToken = data.access_token; // Store in memory
  
  return data;
}

async function getUserProfile() {
  const response = await fetch('/api/v1/user/me', {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
  
  return response.json();
}
```

---

## Security Best Practices

### Token Security

✅ **DO:**
- Use HTTP-only cookies for token storage
- Use HTTPS in production
- Implement token refresh mechanism
- Set appropriate token expiration times
- Use strong secret keys (256-bit)
- Rotate secret keys periodically

❌ **DON'T:**
- Store tokens in localStorage
- Send tokens in URL parameters
- Use weak or predictable secrets
- Share secrets in version control
- Expose tokens in logs

---

### Password Security

✅ **DO:**
- Use bcrypt for password hashing
- Enforce password complexity requirements
- Implement rate limiting on login attempts
- Use secure password reset flow
- Hash passwords before storing

❌ **DON'T:**
- Store plain text passwords
- Use weak hashing algorithms (MD5, SHA1)
- Allow common passwords
- Log passwords
- Send passwords via email

---

### API Security

✅ **DO:**
- Validate all input data
- Use parameterized SQL queries
- Implement rate limiting
- Use CORS properly
- Log security events
- Keep dependencies updated

❌ **DON'T:**
- Trust client input
- Expose sensitive data in errors
- Use wildcard CORS
- Ignore security warnings
- Run with debug mode in production

---

## Token Expiry Policy

| Environment | Access Token | Refresh Token |
| --- | --- | --- |
| **Development** | 30 minutes | 7 days |
| **Production** | 30 minutes | 7 days |
| **Mobile App** | 1 hour | 30 days |

---

## Troubleshooting

### Common Authentication Errors

| Error | Cause | Solution |
| --- | --- | --- |
| `401 Unauthorized` | Token missing or invalid | Check if token is being sent correctly |
| `401 Token expired` | Access token expired | Call `/user/refresh` endpoint |
| `403 Forbidden` | Insufficient permissions | Check user role and required scopes |
| `404 User not found` | Invalid user_id in token | Re-login to get fresh token |
| `400 Invalid credentials` | Wrong email/password | Verify credentials |

---

### Debug Checklist

1. **Token not being sent?**
   - Check if cookies are enabled
   - Verify `credentials: 'include'` in fetch
   - Check CORS configuration

2. **Token expires too quickly?**
   - Implement auto-refresh mechanism
   - Check token expiry settings

3. **Permission denied errors?**
   - Verify user role in database
   - Check scope requirements on endpoint
   - Ensure middleware is working

4. **OTP not received?**
   - Check email configuration
   - Verify email address is correct
   - Check spam folder
   - Check SMTP logs

---

## Configuration

### Environment Variables

```bash
# JWT Settings
SECRET_KEY=your-secret-key-256-bit
REFRESH_SECRET_KEY=your-refresh-secret-key-256-bit
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email Settings (for OTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

---

## Testing Authentication

### Test User Registration

```bash
curl -X POST "http://localhost:8000/user/register" \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "Test",
    "lastName": "User",
    "email": "test@example.com",
    "phoneNo": "9876543210",
    "password": "Test@123",
    "role": "user"
  }'
```

### Test Login

```bash
curl -X POST "http://localhost:8000/user/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "user_email_or_password=test@example.com&password=Test@123" \
  -c cookies.txt
```

### Test Protected Endpoint

```bash
curl -X GET "http://localhost:8000/user/me" \
  -b cookies.txt
```

---

## Monitoring & Logging

### Security Events to Log

- User registration attempts
- Login attempts (success/failure)
- Password change attempts
- Token refresh requests
- Permission denied errors
- Invalid token attempts

### Example Log Entry

```json
{
  "timestamp": "2025-11-15T10:30:00Z",
  "event": "login_attempt",
  "user_email": "john@example.com",
  "ip_address": "192.168.1.100",
  "success": true,
  "user_agent": "Mozilla/5.0..."
}
```

---

**End of Authentication & Role Documentation**