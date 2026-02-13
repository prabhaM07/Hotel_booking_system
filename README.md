# 🏨 Hotel Booking System

A feature-rich, production-ready backend API for hotel management with AI-powered assistance, real-time chat, and advanced search capabilities.

---

## 📑 Table of Contents

- [✨ Features](#-features)
- [🏗️ Architecture](#️-architecture)
- [🛠️ Tech Stack](#️-tech-stack)
- [📋 Prerequisites](#-prerequisites)
- [🚀 Installation](#-installation)
- [⚙️ Configuration](#️-configuration)
- [💾 Database Setup](#-database-setup)
- [🔍 Search System](#-search-system)
- [💬 Real-Time Chat](#-real-time-chat)
- [🤖 RAG System](#-rag-system)
- [🏃 Running the Application](#-running-the-application)
- [📁 Project Structure](#-project-structure)
- [🔐 Authentication](#-authentication)
- [📞 Contact](#-contact)

---

## ✨ Features

### Core Hotel Management
- **User Management**: Registration, authentication with JWT tokens, role-based access control (Admin, Manager, Staff, Customer)
- **Room Management**: Comprehensive inventory with room types, features, pricing, and availability
- **Booking System**: Complete lifecycle management - creation, modification, cancellation, and status tracking
- **Reviews & Ratings**: Customer feedback system with moderation capabilities
- **Add-ons Management**: Extra services (breakfast, spa, tours, transportation)
- **Activity Logging**: Comprehensive audit trails for all system operations

### Advanced Search Capabilities
- **Full-Text Search (FTS)**: PostgreSQL tsvector-based semantic search with ranking
- **Trigram Search**: Fuzzy matching using pg_trgm for typo-tolerant searches
- **Hybrid Search**: Combines multiple search strategies for optimal results
- **Auto-Complete**: Real-time suggestions as users type
- **Multi-Field Search**: Search across rooms, room types, features, bookings, users, and more

### Real-Time Communication
- **WebSocket Chat**: Instant messaging between customers and admin
- **Online Status Tracking**: See who's currently online
- **Chat History**: Persistent message storage in MongoDB
- **Read Receipts**: Track message delivery and read status
- **Multi-User Support**: Handle multiple concurrent chat sessions

### AI-Powered Assistance
- **RAG System**: Retrieval-Augmented Generation for intelligent Q&A
- **Hybrid Retrieval**: Dense (vector) + Sparse (BM25) search
- **Natural Language Queries**: Ask questions in plain English
- **Context-Aware Responses**: Powered by Llama 3.3 70B via Groq
- **Source Citations**: Transparent references for all AI responses

### Background Services
- **Automated Backups**: Daily PostgreSQL and MongoDB backups
- **Analytics Aggregation**: Real-time dashboard data processing
- **Log Rotation**: Automatic cleanup and archiving
- **Scheduled Tasks**: APScheduler for periodic jobs

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT APPLICATIONS                       │
│         (React, Mobile Apps, Admin Dashboard)               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      FASTAPI GATEWAY                         │
│   [Auth] [CORS] [Logging] [Rate Limiting] [WebSocket]      │
└─────────────────────────────────────────────────────────────┘
                              ↓
         ┌────────────────────┴────────────────────┐
         ↓                    ↓                     ↓
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│  BUSINESS LOGIC  │ │  SEARCH ENGINE   │ │   RAG PIPELINE   │
│  - CRUD Ops      │ │  - FTS           │ │  - LangChain     │
│  - Booking       │ │  - Trigram       │ │  - Pinecone      │
│  - Auth Service  │ │  - Hybrid        │ │  - Groq LLM      │
└──────────────────┘ └──────────────────┘ └──────────────────┘
         ↓                    ↓                     ↓
┌─────────────────────────────────────────────────────────────┐
│                      DATA LAYER                              │
│  PostgreSQL (ACID)  |  MongoDB (Docs)  |  Pinecone (Vectors)│
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

### Backend Framework
- **FastAPI** - Modern, high-performance Python web framework
- **Uvicorn** - Lightning-fast ASGI server
- **Python 3.11+** - Latest Python features

### Databases
- **PostgreSQL 14+** - Primary relational database with FTS support
- **MongoDB 6+** - Document store for chat history and flexible schemas
- **Pinecone** - Serverless vector database for semantic search

### Search Technologies
- **PostgreSQL FTS** - Full-text search with tsvector/tsquery
- **pg_trgm Extension** - Trigram matching for fuzzy search
- **GIN Indexes** - Generalized Inverted Index for fast text search

### AI/RAG Components
- **LangChain** - RAG orchestration and chain management
- **HuggingFace** - all-MiniLM-L6-v2 embeddings (384-dim)
- **Pinecone Text** - BM25 sparse encoder for keyword retrieval
- **Groq** - Fast LLM inference (Llama 3.3 70B)

### ORM & Validation
- **SQLAlchemy** - Python SQL toolkit and ORM
- **Pydantic** - Data validation using type hints

### Authentication
- **PyJWT** - JSON Web Token implementation
- **passlib[bcrypt]** - Secure password hashing
- **python-jose** - JOSE implementation for JWT

### Real-Time Communication
- **WebSockets** - Full-duplex communication protocol
- **Motor** - Async MongoDB driver for Python

### Background Processing
- **APScheduler** - Advanced Python scheduler
- **python-dotenv** - Environment management

---

## 📋 Prerequisites

Before installation, ensure you have:

### Required Software
- **Python 3.11 or higher** - [Download](https://www.python.org/downloads/)
- **PostgreSQL 14 or higher** - [Download](https://www.postgresql.org/download/)
- **MongoDB 6 or higher** - [Download](https://www.mongodb.com/try/download/community)
- **Git** - [Download](https://git-scm.com/downloads/)

### API Keys
- **Pinecone API Key** - [Sign up](https://www.pinecone.io/)
- **Groq API Key** - [Get yours](https://console.groq.com/)

### System Requirements
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **OS**: Windows 10+, macOS 10.15+, or Linux

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/hotel-booking-system.git
cd hotel-booking-system
```

### 2. Create Virtual Environment

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install all packages
pip install -r requirements.txt

# Verify installation
python -c "import fastapi, sqlalchemy, motor, pinecone; print('All packages installed!')"
```

---

## Configuration

### Create Environment File

Create a `.env` file in the project root:

```env
# =================================================================
# PostgreSQL Configuration
# =================================================================
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=hotel_booking_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# =================================================================
# MongoDB Configuration
# =================================================================
MONGO_URL=mongodb://localhost:27017
MONGO_DB=hotel_booking_db

# =================================================================
# JWT Token Configuration
# =================================================================
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=your_secret_key_here
REFRESH_SECRET_KEY=your_refresh_secret_key_here

# =================================================================
# RAG System Configuration
# =================================================================
GROQ_API_KEY=your_groq_api_key
PINECONE_API_KEY=your_pinecone_api_key

# =================================================================
# CORS Configuration
# =================================================================
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# =================================================================
# Server Configuration
# =================================================================
ENVIRONMENT=development
HOST=127.0.0.1
PORT=8000
RELOAD=True
APP_NAME=HotelBookingSystem
```

### Generate Secret Keys

```bash
# Generate SECRET_KEY
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"

# Generate REFRESH_SECRET_KEY
python -c "import secrets; print('REFRESH_SECRET_KEY=' + secrets.token_hex(32))"
```

---

## 💾 Database Setup

### PostgreSQL Setup

#### 1. Start PostgreSQL Service

**Windows:**
```cmd
net start postgresql-x64-14
```

**Linux (Ubuntu/Debian):**
```bash
sudo systemctl start postgresql
```

**macOS:**
```bash
brew services start postgresql
```

#### 2. Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE hotel_booking_db;

# Exit
\q
```

#### 3. Verify Connection

```bash
psql -U postgres -d hotel_booking_db -c "SELECT version();"
```

### MongoDB Setup

#### 1. Start MongoDB Service

**Windows:**
```cmd
net start MongoDB
```

**Linux (Ubuntu/Debian):**
```bash
sudo systemctl start mongod
```

**macOS:**
```bash
brew services start mongodb-community
```

#### 2. Verify MongoDB

```bash
mongosh --eval "db.version()"
```

### Database Initialization

The application automatically creates tables, indexes, and triggers on first run:

```bash
python -m app.main
```

---

## Search System

The system implements a sophisticated **hybrid search architecture** combining multiple search strategies:

### 1. Full-Text Search (FTS)

PostgreSQL's native FTS with weighted ranking:

```sql
-- Search vector with weights
setweight(to_tsvector('english', room_name), 'A') ||  -- Highest priority
setweight(to_tsvector('english', features), 'B') ||   -- Medium priority
setweight(to_tsvector('english', description), 'C')   -- Lower priority
```

**Features:**
- Semantic understanding of queries
- Ranking by relevance
- Support for English language stemming
- GIN indexes for performance

### 2. Trigram Search (pg_trgm)

Fuzzy matching for typo-tolerant searches:

```sql
-- Trigram similarity search
SELECT * FROM rooms 
WHERE search_text % 'delux suite'  -- Matches "deluxe suite"
ORDER BY similarity(search_text, 'delux suite') DESC;
```

**Features:**
- Handles misspellings (delux → deluxe)
- Partial word matching
- Fast performance with GIN trigram indexes
- Configurable similarity thresholds

### 3. Search Triggers

Automatic search index updates:

```python
# Rooms search vector trigger
CREATE TRIGGER trg_update_rooms_search_vector
BEFORE INSERT OR UPDATE ON rooms
FOR EACH ROW EXECUTE FUNCTION update_rooms_search_vector();

# Rooms trigram trigger
CREATE TRIGGER trg_update_rooms_search_text
BEFORE INSERT OR UPDATE ON rooms
FOR EACH ROW EXECUTE FUNCTION update_rooms_search_text();
```

### 4. Supported Search Entities

- **Rooms**: room_no, floor, type, price, features, bed types, status
- **Room Types**: name, price, capacity, features, bed types
- **Bookings**: booking_id, customer name, dates, status
- **Users**: name, email, role, phone
- **Features**: feature names and descriptions
- **Add-ons**: addon names, prices, categories
- **Bed Types**: bed type names and sizes
- **Floors**: floor numbers and names


---

## Real-Time Chat

WebSocket-based real-time communication system for customer support.

### Features

- **Instant Messaging**: Real-time message delivery
- **Online Status**: Track who's currently online
- **Persistent History**: Messages stored in MongoDB
- **Role-Based Chat**: Customers ↔ Admin communication
- **Read Receipts**: Track message delivery and read status
- **Connection Management**: Automatic reconnection handling

### Architecture

```
┌─────────────┐         WebSocket          ┌─────────────┐
│   Customer  │ ←─────────────────────────→ │    Admin    │
└─────────────┘                             └─────────────┘
      ↓                                            ↓
      └──────────────────┬──────────────────────┘
                         ↓
                ┌─────────────────┐
                │ ConnectionManager│
                └─────────────────┘
                         ↓
                ┌─────────────────┐
                │    MongoDB      │
                │  (Chat History) │
                └─────────────────┘
```

### Connection Flow

1. **Client connects** with JWT token in cookies
2. **Server validates** token and extracts user info
3. **Connection established** in ConnectionManager
4. **Online status broadcast** to all connected users
5. **Chat history loaded** for the user
6. **Real-time messaging** begins

### Message Format

#### Incoming Message
```json
{
    "type": "message",
    "message": "Hello!",
    "sender_role": "user",
    "sender_id": 42,
    "sender_username": "John Doe",
    "receiver_id": 0,
    "_id": "abc123",
    "timestamp": "2025-01-15T10:30:00Z",
    "seen": false
}
```

#### System Message
```json
{
    "type": "system",
    "message": "Connected as USER - john@example.com (ID: 42)"
}
```

#### Online Status Update
```json
{
    "type": "online_users",
    "users": {
        "1": {"user_id": 1, "email": "admin@hotel.com", "role": "admin"}
    }
}
```

### Access Chat UI

- **Customer Chat**: `http://localhost:8000/api/chat/chat` (requires active booking)
- **Admin Chat**: `http://localhost:8000/api/chat/chat` (admin dashboard)

### Security

- **JWT Authentication**: Token required in cookies
- **Role-Based Access**: Customers can only chat with admin
- **Booking Validation**: Customers must have confirmed booking
- **Connection Limits**: Prevents abuse

---

## RAG System

Intelligent question-answering using Retrieval-Augmented Generation.

### How It Works

1. **Query Processing**: User asks a question in natural language
2. **Hybrid Retrieval**: 
   - Dense search using vector embeddings
   - Sparse search using BM25 keyword matching
3. **Context Assembly**: Retrieved documents are formatted
4. **LLM Generation**: Llama 3.3 70B generates answer with context
5. **Response**: Answer with source citations

### Setup

```python
# Initialize RAG system
from app.services.rag_service import initialize_rag_system

# Add documents to knowledge base
await initialize_rag_system()
```

## 🏃 Running the Application

### Development Mode

```bash
# Using uvicorn (with auto-reload)
uvicorn app.main:application --reload --host 0.0.0.0 --port 8000

# OR using the main script
python main.py
```

##  Project Structure

```
hotel-booking-system/
│
├── app/                          # Main application package
│   ├── __init__.py
│   ├── main.py                   # FastAPI app entry point
│   │
│   ├── core/                     # Core configuration
│   │   ├── config.py             # Settings (Pydantic)
│   │   ├── database_postgres.py  # PostgreSQL connection
│   │   ├── database_mongo.py     # MongoDB connection
│   │   └── dependency.py         # Dependency injection
│   │
│   ├── auth/                     # Authentication
│   │   ├── jwt_handler.py        # JWT encode/decode
│   │   ├── jwt_bearer.py         # JWT dependency
│   │   ├── auth_utils.py         # Password utilities
│   │   └── hashing.py            # Bcrypt hashing
│   │
│   ├── models/                   # SQLAlchemy models
│   │   ├── user.py
│   │   ├── room.py
│   │   ├── booking.py
│   │   ├── review.py
│   │   └── ...
│   │
│   ├── schemas/                  # Pydantic schemas
│   │   ├── user_schema.py
│   │   ├── room_schema.py
│   │   └── ...
│   │
│   ├── routes/                   # API routes
│   │   ├── auth_routes.py        # /api/auth/*
│   │   ├── users.py              # /api/users/*
│   │   ├── rooms.py              # /api/rooms/*
│   │   ├── ...
│   │
│   ├── crud/                     # Database operations
│   │   ├── user_crud.py
│   │   ├── room_crud.py
│   │   └── ...
│   │
│   ├── middleware/               # Middleware
│   │   ├── logging_middleware.py
│   │   └── auth_middleware.py
│   │
│   ├── services/                 # Business logic
│   │   ├── scheduler.py          # Background tasks
│   │
│   ├── backups/                  # Backup storage
|   |   |── mongoDB/
│   │   └── postgressDB/
│   │
│   ├── static/                   # Static files
│   │   ├── images/
│   │
│   ├── templates/                # HTML templates
│   │   ├── admin_chat.html
│   │   ├── user_chat.html
│   │
│   └── logs/                     # Application logs
│       ├── activity.log
│
├── .env                          # Environment variables
├── .env.example                  # Example env file
├── .gitignore
├── requirements.txt              # Dependencies
├── README.md                     # This file
└── LICENSE
```

---

##  Authentication

### JWT Token Flow

```
1. User logs in → Server validates credentials
2. Server generates JWT tokens:
   - Access Token (30 min) - stored in HTTP-only cookie
   - Refresh Token (7 days) - stored in HTTP-only cookie
3. Client includes cookies in subsequent requests
4. Middleware validates access token
5. Access token expires → Use refresh token to get new access token
```

### Role-Based Access Control (RBAC)

| Role     | Permissions |
|----------|------------|
| **Admin** | Full system access, user management, backups |
| **Manager** | Booking management, room management |
| **Staff** | View bookings, update room status |
| **Customer** | Create bookings, submit reviews, chat |

### Protected Route Example

```python
from app.auth.jwt_bearer import JWTBearer

@router.get("/protected")
async def protected_route(
    request: Request,
    dependencies=[Depends(JWTBearer(required_roles=["admin", "manager"]))]
):
    current_user = request.state.user
    return {"message": f"Hello {current_user.email}"}
```

---

### Database Optimization

```sql
-- Create composite indexes for common queries
CREATE INDEX idx_bookings_user_status ON bookings(user_id, booking_status);
CREATE INDEX idx_rooms_type_status ON rooms(room_type_id, status);

-- Analyze tables for query planner
ANALYZE rooms;
ANALYZE bookings;
ANALYZE users;

-- Vacuum to reclaim space
VACUUM ANALYZE;
```

### Caching Strategy

```python
from functools import lru_cache
```

### Connection Pooling

```python
# In database_postgres.py
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

---

## Security Best Practices

### Environment Variables
- Never commit `.env` to version control
- Use different secrets for dev/staging/prod
- Rotate secrets regularly

### Password Security
- Minimum 8 characters
- Bcrypt hashing with salt
- Rate limiting on login attempts

### SQL Injection Prevention
- Use SQLAlchemy ORM (parameterized queries)
- Input validation with Pydantic
- Escape user inputs


### CORS Configuration
```python
# Only allow trusted origins
ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://admin.yourdomain.com"
]
```

---

## Monitoring & Logging

### Application Logs

```
app/logs/
├── access.log      # HTTP requests
├── error.log       # Errors and exceptions
├── chat.log        # WebSocket activity
└── search.log      # Search queries
```

---

## Backup & Restore

### Automated Backups

Scheduled daily backups via APScheduler:

```python

scheduler.add_job(
    backup_databases,
    'cron',
    hour=2,
    minute=0
)
```

### Manual Backup

#### PostgreSQL
```bash
# Create backup
pg_dump -U postgres hotel_booking_db > backup_$(date +%Y%m%d).sql

# Restore backup
psql -U postgres hotel_booking_db < backup_20250115.sql
```

#### MongoDB
```bash
# Create backup
mongodump --db hotel_booking_db --out ./backup

# Restore backup
mongorestore --db hotel_booking_db ./backup/hotel_booking_db
```

## 📞 Contact

**Developer**: Prabha

- **Email**: prabhamuruganantham06@gmail.com

