# ShopEase – Standalone Authentication Microservice

## 1. Project Overview

ShopEase Authentication Microservice is an independent backend application developed using Python and FastAPI.

The application provides secure user registration, login, password hashing, JWT-based authentication, access-token verification, authenticated user-profile retrieval, and password changes.

It uses its own MySQL database and is containerized using Docker and Docker Compose.

This is a standalone service developed independently before any integration with other ShopEase microservices.

## 2. Project Objectives

The main objectives are:

- Develop an independent Authentication Microservice using FastAPI.
- Implement user registration and login.
- Store passwords securely using bcrypt hashing.
- Generate and validate JWT access tokens.
- Protect APIs using Bearer token authentication.
- Connect to a dedicated MySQL database using SQLAlchemy ORM.
- Manage database schema changes using Alembic.
- Containerize the application and database using Docker.
- Test successful and unsuccessful authentication scenarios.
- Maintain project documentation and source code using Git and GitHub.

## 3. Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.11 | Backend programming |
| FastAPI | REST API development |
| Uvicorn | ASGI application server |
| MySQL 8.0 | Database |
| SQLAlchemy | ORM and database operations |
| Alembic | Database migrations |
| Pydantic | Request and response validation |
| PyJWT | JWT creation and verification |
| Passlib | Password hashing management |
| bcrypt | Secure password hashing |
| Docker | Application containerization |
| Docker Compose | Multi-container management |
| Swagger UI | API documentation and testing |
| Git | Version control |
| GitHub | Source-code hosting |

## 4. Project Architecture

```text
                 CLIENT
             Swagger / Postman
                    |
                    v
          FASTAPI APPLICATION
                    |
                    v
          AUTHENTICATION ROUTER
                    |
                    v
          AUTHENTICATION SERVICE
             /           \
            v             v
       SECURITY        SQLAlchemy
       JWT/Bcrypt          |
                           v
                     MYSQL DATABASE
                           |
                           v
                    ALEMBIC MIGRATIONS
```

### Architecture Components

**FastAPI Application**
- Provides the application entry point.
- Registers authentication routes.
- Exposes health-check endpoints.

**Authentication Router**
- Receives HTTP requests.
- Validates request data through Pydantic schemas.
- Calls the authentication service.
- Returns appropriate HTTP responses.

**Authentication Service**
- Implements registration and login logic.
- Checks duplicate email addresses.
- Retrieves user information.
- Verifies authenticated users.
- Handles password changes.

**Security Module**
- Hashes and verifies passwords using bcrypt.
- Generates JWT access tokens.
- Validates token signatures and expiration.

**SQLAlchemy**
- Provides database connectivity.
- Manages database sessions.
- Maps Python models to MySQL tables.

**Alembic**
- Tracks database schema changes.
- Generates migration scripts.
- Applies and manages database migrations.

## 5. Project Structure

```text
shopease-auth-service/
|
|-- app/
|   |
|   |-- main.py
|   |
|   |-- routers/
|   |   |-- __init__.py
|   |   |-- auth_routes.py
|   |
|   |-- models/
|   |   |-- __init__.py
|   |   |-- user_model.py
|   |
|   |-- schemas/
|   |   |-- __init__.py
|   |   |-- auth_schema.py
|   |
|   |-- services/
|   |   |-- __init__.py
|   |   |-- auth_service.py
|   |
|   |-- core/
|   |   |-- __init__.py
|   |   |-- config.py
|   |   |-- security.py
|   |
|   |-- database/
|       |-- __init__.py
|       |-- connection.py
|
|-- alembic/
|   |-- versions/
|   |   |-- create_users_table.py
|   |-- env.py
|   |-- script.py.mako
|
|-- alembic.ini
|-- Dockerfile
|-- docker-compose.yml
|-- requirements.txt
|-- .env
|-- .env.example
|-- .dockerignore
|-- .gitignore
|-- README.md
```

## 6. Database Design

**Database:** `shopease_auth_db`

**Table:** `users`

| Column | Data Type | Description |
|---|---|---|
| id | Integer | Primary key and unique user ID |
| full_name | VARCHAR(150) | User's full name |
| email | VARCHAR(255) | Unique email address |
| password_hash | VARCHAR(255) | Bcrypt password hash |
| role | VARCHAR(30) | User role |
| is_active | Boolean | Account activation status |
| created_at | DATETIME | Account creation timestamp |
| updated_at | DATETIME | Last update timestamp |

### Database Features

- The user ID is an auto-incrementing primary key.
- Email addresses are unique.
- Passwords are stored as bcrypt hashes.
- New users receive the default role `CUSTOMER`.
- New accounts are active by default.
- Creation and update timestamps are maintained.

### Database Migration

Alembic manages the database schema.

The initial migration creates the `users` table and the `alembic_version` table.

The applied migration revision is recorded by Alembic.

## 7. Authentication API Endpoints

**Base URL:**

`http://localhost:8011`

**Swagger UI:**

`http://localhost:8011/docs`

| HTTP Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Register a new user |
| POST | `/api/auth/login` | Authenticate a user and generate JWT |
| GET | `/api/auth/me` | Retrieve authenticated user profile |
| POST | `/api/auth/verify-token` | Verify an access token |
| POST | `/api/auth/change-password` | Change authenticated user's password |

### 7.1 User Registration

**Endpoint:** `POST /api/auth/register`

Request:

```json
{
  "full_name": "Ravi Kumar",
  "email": "ravi@example.com",
  "password": "ShopEase@2026",
  "confirm_password": "ShopEase@2026"
}
```

Expected response status: `201 Created`.

Registration functionality:

- Validates the full name.
- Validates email format.
- Checks password requirements.
- Checks password confirmation.
- Rejects duplicate email addresses.
- Hashes the password using bcrypt.
- Assigns the default role `CUSTOMER`.
- Saves the user in MySQL.
- Returns safe user information without password details.

### 7.2 User Login

**Endpoint:** `POST /api/auth/login`

Request:

```json
{
  "email": "ravi@example.com",
  "password": "ShopEase@2026"
}
```

Expected response status: `200 OK`.

Login functionality:

- Retrieves the user using the email address.
- Verifies the entered password against the stored bcrypt hash.
- Rejects incorrect credentials.
- Rejects inactive accounts.
- Generates a signed JWT access token.
- Returns the access token and safe user information.

### 7.3 Get Current User

**Endpoint:** `GET /api/auth/me`

Authorization header:

```text
Authorization: Bearer YOUR_ACCESS_TOKEN
```

Expected response status: `200 OK`.

Returns authenticated user information, including:

- User ID
- Full name
- Email
- Role
- Account status
- Creation timestamp
- Update timestamp

### 7.4 Verify Access Token

**Endpoint:** `POST /api/auth/verify-token`

Request:

```json
{
  "access_token": "YOUR_ACCESS_TOKEN"
}
```

Expected response for a valid token:

```json
{
  "valid": true,
  "message": "Access token is valid",
  "user_id": 1,
  "role": "CUSTOMER"
}
```

The actual user ID depends on the database record.

### 7.5 Change Password

**Endpoint:** `POST /api/auth/change-password`

Authorization header:

```text
Authorization: Bearer YOUR_ACCESS_TOKEN
```

Request:

```json
{
  "current_password": "ShopEase@2026",
  "new_password": "ShopEase@2027"
}
```

Expected response status: `200 OK`.

Password-change functionality:

- Requires a valid authenticated user.
- Verifies the current password.
- Validates the new password.
- Hashes the new password.
- Updates the password hash in MySQL.

Previously issued JWT access tokens remain valid until their expiration unless separately revoked.

## 8. Password Security

Passwords are hashed using bcrypt through Passlib.

Original passwords are never stored in the database.

### Password Validation Rules

- Minimum 8 characters.
- At least one uppercase letter.
- At least one lowercase letter.
- At least one number.
- At least one special character.
- Maximum 72 UTF-8 bytes for bcrypt compatibility.

The application uses:

```python
hash_password(password)
```

to create password hashes and:

```python
verify_password(password, stored_hash)
```

to verify passwords during login.

## 9. JWT Authentication

The application uses JSON Web Tokens for authentication.

JWT payload contains:

| Claim | Description |
|---|---|
| sub | User ID |
| role | User role |
| iat | Issued-at timestamp |
| exp | Expiration timestamp |

### Token Generation

JWT tokens are generated after successful login using the configured secret key and signing algorithm.

### Token Validation

The application checks:

- JWT signature.
- Signing algorithm.
- Required claims.
- Expiration time.
- User existence.
- User account activation status.
- Consistency between the token role and current database role.

### Protected Endpoints

The `/me` and `/change-password` endpoints require Bearer token authentication.

## 10. Environment Configuration

The application uses a `.env` file for configuration.

Important variables:

```env
APP_NAME=ShopEase Standalone Authentication Service
APP_ENV=development

DB_HOST=auth_mysql
DB_PORT=3306
DB_NAME=shopease_auth_db
DB_USER=shopease_auth_user
DB_PASSWORD=YOUR_DATABASE_PASSWORD

MYSQL_ROOT_PASSWORD=YOUR_ROOT_PASSWORD
MYSQL_DATABASE=shopease_auth_db
MYSQL_USER=shopease_auth_user
MYSQL_PASSWORD=YOUR_DATABASE_PASSWORD

JWT_SECRET_KEY=YOUR_LONG_RANDOM_SECRET
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Security:** The values above are placeholders. Use your own secure credentials.

The real `.env` file must never be committed to Git or uploaded to GitHub.

The `.env.example` file provides a template without actual credentials.

## 11. Docker Configuration

The project runs two separate Docker services.

| Container | Service | Host Port | Container Port |
|---|---|---:|---:|
| `shopease_auth_service_standalone` | FastAPI | 8011 | 8000 |
| `shopease_auth_mysql_standalone` | MySQL 8.0 | 3310 | 3306 |

### Docker Features

- Dedicated FastAPI container.
- Separate MySQL container.
- Docker Compose networking.
- MySQL healthcheck.
- API startup dependency on healthy MySQL.
- Persistent named MySQL volume.
- Environment-based configuration.

### Database Storage

Docker named volume:

`shopease-auth-service_shopease_auth_mysql_data`

This preserves MySQL data when containers are restarted or recreated without removing the volume.

## 12. Run the Application

### Prerequisites

- Docker Desktop.
- Docker Compose.
- Git.
- PowerShell.

### Step 1 – Open the project folder

```powershell
cd C:\shopease-auth-service
```

### Step 2 – Configure environment

Create `.env` using the provided configuration template and supply secure credentials.

### Step 3 – Build the application image

```powershell
docker compose build auth_service
```

### Step 4 – Start the containers

```powershell
docker compose up -d
```

### Step 5 – Check container status

```powershell
docker compose ps
```

Both the API and MySQL containers should be running. MySQL should report a healthy status.

### Step 6 – Check API health

```powershell
Invoke-RestMethod http://localhost:8011/health
```

### Step 7 – Open Swagger

`http://localhost:8011/docs`

Use Swagger UI to execute and test the authentication APIs.

## 13. Database Management Using Alembic

Alembic manages database schema changes.

### Generate a Migration

```powershell
docker compose exec auth_service alembic revision --autogenerate -m "describe database change"
```

Review the generated migration file before applying it.

### Apply Migrations

```powershell
docker compose exec auth_service alembic upgrade head
```

### Check Current Migration

```powershell
docker compose exec auth_service alembic current
```

### View Migration History

```powershell
docker compose exec auth_service alembic history
```

Alembic uses the `alembic_version` table to maintain migration revision information.

## 14. API Testing

The application was tested through Swagger UI and Docker-based execution.

### Successful Test Scenarios

- User registration.
- User login with correct credentials.
- Current-user profile retrieval.
- Access-token verification.
- Password change with correct current password.
- Login using the updated password.
- MySQL connectivity.
- Alembic migration execution.
- Docker container startup and health checks.

### Negative Test Scenarios

- Duplicate email registration.
- Invalid email address.
- Password and confirmation mismatch.
- Incorrect login credentials.
- Login with an inactive account.
- Accessing a protected endpoint without a token.
- Accessing a protected endpoint with an invalid token.
- Expired JWT.
- Password change with incorrect current password.

### Expected HTTP Status Codes

| Status | Meaning | Example |
|---|---|---|
| 200 | OK | Successful login or profile retrieval |
| 201 | Created | Successful registration |
| 400 | Bad Request | Incorrect current password |
| 401 | Unauthorized | Invalid credentials or token |
| 403 | Forbidden | Inactive user |
| 404 | Not Found | User not found |
| 409 | Conflict | Duplicate email |
| 422 | Unprocessable Entity | Invalid input validation |

## 15. Docker Management Commands

### View Running Containers

```powershell
docker compose ps
```

### View API Logs

```powershell
docker compose logs auth_service
```

### View MySQL Logs

```powershell
docker compose logs auth_mysql
```

### Stop Containers

```powershell
docker compose stop
```

### Start Existing Containers

```powershell
docker compose start
```

### Restart Containers

```powershell
docker compose restart
```

**Important:** Avoid `docker compose down -v` during normal development because the `-v` option removes the persistent database volume and can delete stored data.

## 16. Git and GitHub

Git is used to maintain project history and track code changes.

The source code is intended to be maintained in a GitHub repository named:

`shopease-auth-service`

Sensitive files such as `.env` must be excluded from Git commits.

The project includes `.gitignore` and `.dockerignore` configuration files to avoid exposing secrets and temporary files.

## 17. Learning Outcomes

Through this project, the following backend development concepts were implemented and practiced:

1. Understanding independent microservice architecture.
2. Building REST APIs using FastAPI.
3. Separating routers, services, models, schemas and security logic.
4. Validating request data using Pydantic.
5. Connecting MySQL using SQLAlchemy ORM.
6. Managing database sessions and transactions.
7. Creating and maintaining database migrations using Alembic.
8. Hashing and verifying passwords using bcrypt.
9. Generating and validating JWT access tokens.
10. Implementing reusable authentication dependencies.
11. Handling authentication errors and HTTP status codes.
12. Containerizing applications using Docker.
13. Managing application and database containers using Docker Compose.
14. Testing APIs using Swagger UI.
15. Maintaining source code using Git and GitHub.

## 18. Future Enhancements

Possible future improvements include:

- Automated unit and integration testing using Pytest.
- Refresh-token implementation.
- Token revocation or token-version management.
- Role-based authorization.
- Email verification.
- Forgot-password and password-reset workflows.
- Login rate limiting and brute-force protection.
- Structured application logging.

## 19. Project Independence

This is an independent Authentication Microservice with its own FastAPI application, MySQL database, SQLAlchemy models, Alembic migration history and Docker environment.

It is not combined with the separate Product Service assignment or the integrated ShopEase microservices project.

The application is developed and tested independently before any future service integration.

---

**Project Name:** ShopEase – Standalone Authentication Microservice

**Backend:** Python and FastAPI

**Database:** MySQL 8.0

**Authentication:** JWT and bcrypt

**Database Migration:** Alembic

**Containerization:** Docker and Docker Compose

**Local API Address:** http://localhost:8011

**Swagger Documentation:** http://localhost:8011/docs
