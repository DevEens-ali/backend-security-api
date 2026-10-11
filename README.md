# Backend Security API

A secure REST API built with **FastAPI, MySQL, SQLAlchemy, JWT Authentication, and Role-Based Access Control (RBAC)**. This project demonstrates secure authentication, authorization, refresh-token rotation, rate limiting, input validation, and automated testing.

## Features

- User registration and login with bcrypt password hashing.
- JWT access tokens with a 15-minute lifetime.
- Refresh tokens with a 7-day lifetime.
- Refresh-token rotation and revocation.
- HTTP-only cookies for refresh tokens.
- Role-Based Access Control with Admin, Moderator, and User roles.
- Login rate limiting: 5 attempts per IP address per 60-second window.
- Pydantic request validation.
- Automated tests using pytest.
- Interactive Swagger API documentation.

## Tech Stack

- Python
- FastAPI
- MySQL
- SQLAlchemy
- PyMySQL
- Pydantic
- PyJWT
- bcrypt
- pytest
- HTTPX

## Project Structure

```text
backend-security-api/
├── app/
│   ├── dependencies/
│   │   ├── auth.py
│   │   └── rbac.py
│   ├── middleware/
│   │   └── rate_limiter.py
│   ├── routers/
│   │   ├── auth.py
│   │   └── users.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── rate_limit_service.py
│   │   └── token_service.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
├── tests/
│   ├── test_auth.py
│   ├── test_rate_limit.py
│   └── test_rbac.py
├── .gitignore
├── requirements.txt
└── README.md
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/DevEens-ali/backend-security-api.git
cd backend-security-api
```

### 2. Create a Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Create the MySQL Database

```sql
CREATE DATABASE backend_security_db;
```

### 5. Configure Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=mysql+pymysql://YOUR_DB_USER:YOUR_DB_PASSWORD@localhost:3306/backend_security_db
SECRET_KEY=your_long_random_secret_key
```

Replace the placeholders with your own local database credentials and a strong secret key.

**Security:** Never commit your `.env` file or expose database credentials and secret keys.

### 6. Run the Application

```bash
uvicorn app.main:app --reload
```

Open the following URLs:

- **API:** http://127.0.0.1:8000
- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

Ensure that the database tables are created using the project's configured table-creation process or migrations.

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Authenticate and issue tokens |
| POST | `/auth/refresh` | Rotate the refresh token |
| POST | `/auth/logout` | Revoke the refresh token and clear its cookie |

### User and RBAC Endpoints

| Method | Endpoint | Access |
|---|---|---|
| GET | `/users/me` | Authenticated users |
| GET | `/users/admin-only` | Admin |
| GET | `/users/moderator-only` | Moderator or Admin |
| GET | `/users/user-area` | User or Admin |

## Role-Based Access Control

- **Admin:** Can access admin-only routes, moderator routes, and the user area.
- **Moderator:** Can access moderator routes but cannot access admin-only routes or the user area.
- **User:** Can access their own profile and the user area but cannot access admin-only or moderator-only routes.

Protected endpoints use bearer access tokens:

```http
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## Rate Limiting

Login requests are limited to **5 attempts per IP address within 60 seconds**. Additional requests receive `429 Too Many Requests` and a `Retry-After` header.

The current limiter uses in-memory storage. A shared store such as Redis is recommended for deployments with multiple workers or instances.

## Testing

Run the automated test suite:

```bash
python -m pytest -v
```

Tests cover authentication validation, refresh-token behavior, role-based permissions, and login rate limiting.

## Security Considerations

- Use a strong secret key stored in environment variables.
- Enable HTTPS in production.
- Configure refresh cookies with `Secure`, `HttpOnly`, and an appropriate `SameSite` policy.
- Never commit `.env` or expose credentials.
- Use database migrations for production schema changes.
- Never log passwords or authentication tokens.

## Author

**Anees Ali**

- GitHub: [DevEens-ali](https://github.com/DevEens-ali/)
- Repository: [Backend Security API](https://github.com/DevEens-ali/backend-security-api)

---

Developed to practice backend API security, authentication, authorization, token management, and automated testing.
