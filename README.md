# FastAPI - Base Project (Modular) with Authentication

This is a minimal base project structure for a scalable FastAPI application organized per-module with JWT authentication.

## Setup

1. Copy environment file:
```bash
cp .env.example .env
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start MongoDB (local or Docker):
```bash
# Using Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Or install MongoDB locally
```

4. Run the application:
```bash
uvicorn app.main:app --reload
```

5. Access API docs: http://127.0.0.1:8000/docs

## Authentication Flow

### 1. Register User
```bash
POST /api/v1/users/
{
  "email": "user@example.com",
  "password": "password123",
  "name": "User Name"
}
```

### 2. Login
```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

Response:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

### 3. Use Protected Endpoints

#### Option A: Manual API calls
Include the access token in Authorization header:
```
Authorization: Bearer eyJ...
```

#### Option B: Swagger UI Authorization
1. Go to http://127.0.0.1:8000/docs
2. Click the **"Authorize"** button (lock icon) at the top
3. In the "Value" field, enter just the token string: `eyJ...` (without "Bearer " prefix)
4. Click **"Authorize"**
5. Now all protected endpoints will automatically include the token

### 4. Refresh Token
```bash
POST /api/v1/auth/refresh
{
  "refresh_token": "eyJ..."
}
```

## Project Structure

- `app/main.py`: application factory / entrypoint
- `app/api/v1/auth.py`: authentication endpoints (login, refresh)
- `app/api/v1/users.py`: user CRUD endpoints (protected)
- `app/schemas/`: pydantic models (user, auth)
- `app/services/`: business logic (user service, auth service)
- `app/db/`: MongoDB connection setup
- `app/core/config.py`: JWT and DB configuration
- `app/api/deps.py`: database dependency injection

## Security Features

- Password hashing with bcrypt
- JWT access tokens (60 min expiry)
- JWT refresh tokens (7 days expiry)
- Protected routes with Bearer token authentication
- User registration without authentication
- All user operations require authentication

## Next Steps

- Add role-based authorization
- Implement password reset functionality
- Add email verification
- Add rate limiting
- Add comprehensive tests
- Add CI/CD pipeline
