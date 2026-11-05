cd C:\shopease-auth-service

@'
# ShopEase – Standalone Authentication Microservice

## 1. Project Overview

ShopEase Authentication Microservice is an independent backend service developed using Python and FastAPI.

It provides secure user registration, login, password hashing, JWT authentication, token verification, user profile access, and password changes.

The service uses its own MySQL database and runs independently using Docker Compose.

## 2. Technologies Used

- Python 3.11
- FastAPI
- Uvicorn
- MySQL 8.0
- SQLAlchemy ORM
- Alembic
- Pydantic
- PyJWT
- Passlib and bcrypt
- Docker
- Docker Compose
- Swagger UI
- Git and GitHub

## 3. Project Architecture

```text
Client (Swagger UI / Postman)
              |
              v
       FastAPI Application
              |
              v
       Authentication Router
              |
              v
       Authentication Service
          /          \
         v            v
    Security       SQLAlchemy
    (JWT/Bcrypt)       |
                      v
                 MySQL Database
                      |
                      v
                Alembic Migrations