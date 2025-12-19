# Product Review API - FastAPI + MongoDB

A simple REST API for product reviews built with FastAPI, MongoDB, and JWT authentication. Users can register, login, and manage products with review functionality.

## Features

- 🔐 **JWT Authentication** - Secure login with access and refresh tokens
- 👤 **User Management** - User registration and profile management
- 📦 **Product Management** - CRUD operations for products
- ⭐ **Review System** - Product reviews and ratings
- 📊 **MongoDB Integration** - NoSQL database for flexible data storage
- 📚 **Auto-generated API Docs** - Interactive Swagger UI documentation

## Tech Stack

- **Backend**: FastAPI (Python async web framework)
- **Database**: MongoDB with Motor (async driver)
- **Authentication**: JWT tokens with bcrypt password hashing
- **Validation**: Pydantic models
- **Documentation**: OpenAPI/Swagger UI

## Setup

### Prerequisites

- Python 3.8+
- MongoDB (local or cloud instance)

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd fastapi-mongodb
```

2. **Create virtual environment:**
```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Environment configuration:**
```bash
cp .env.example .env
# Edit .env with your MongoDB URI and JWT settings
```

5. **Start MongoDB:**
```bash
# Using Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Or using local MongoDB installation
mongod
```

6. **Run the application:**
```bash
uvicorn app.main:app --reload
```

7. **Access API documentation:**
   - Swagger UI: http://127.0.0.1:8000/docs
   - ReDoc: http://127.0.0.1:8000/redoc

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token

### Users
- `POST /api/v1/users/` - Register new user
- `GET /api/v1/users/` - List all users (authenticated)
- `GET /api/v1/users/{user_id}` - Get user details (authenticated)
- `PUT /api/v1/users/{user_id}` - Update user (authenticated)
- `DELETE /api/v1/users/{user_id}` - Delete user (authenticated)

### Products
- `POST /api/v1/products/` - Add product
- `GET /api/v1/products/` - List products
- `GET /api/v1/products/{product_id}` - Get product details
- `PUT /api/v1/products/{product_id}` - Update product
- `DELETE /api/v1/products/{product_id}` - Delete product

### Reviews (Coming Soon)
- `POST /api/v1/products/{product_id}/reviews` - Add review
- `GET /api/v1/products/{product_id}/reviews` - Get product reviews
- `PUT /api/v1/reviews/{review_id}` - Update review
- `DELETE /api/v1/reviews/{review_id}` - Delete review

## Security Features

- 🔒 **Password Hashing**: bcrypt for secure password storage
- 🎫 **JWT Tokens**: Access tokens (30 min) and refresh tokens (7 days)
- 🛡️ **Protected Routes**: Bearer token authentication required
- 🔐 **Secure Registration**: Password validation and hashing
- 🚫 **Unauthorized Access Prevention**: Token validation on all protected endpoints

## Development

### API Documentation
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
- **OpenAPI JSON**: http://127.0.0.1:8000/openapi.json

## Environment Variables

Create a `.env` file based on `.env.example`:

```env
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=product_review_db

# JWT Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
