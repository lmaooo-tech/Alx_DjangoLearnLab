# API Authentication Endpoints Documentation

## Base URL
All authentication endpoints are available at: `/api/auth/`

## Endpoints Overview

### 1. User Registration
- **URL**: `/api/auth/register/`
- **Method**: `POST`
- **Authentication**: Not required (AllowAny)
- **Request Body**:
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepassword123",
  "password_confirm": "securepassword123",
  "first_name": "John",
  "last_name": "Doe",
  "bio": "Welcome to my profile"
}
```
- **Response** (201 Created):
```json
{
  "message": "User registered successfully",
  "token": "9944b09199c62bcf9418ad846dd0e4bbea6f3ba4",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "bio": "Welcome to my profile",
    "profile_picture": null,
    "followers_count": 0,
    "following_count": 0,
    "created_at": "2026-02-21T10:30:00Z",
    "updated_at": "2026-02-21T10:30:00Z"
  }
}
```

### 2. User Login
- **URL**: `/api/auth/login/`
- **Method**: `POST`
- **Authentication**: Not required (AllowAny)
- **Request Body**:
```json
{
  "username": "johndoe",
  "password": "securepassword123"
}
```
- **Response** (200 OK):
```json
{
  "message": "Login successful",
  "token": "9944b09199c62bcf9418ad846dd0e4bbea6f3ba4",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "bio": "Welcome to my profile",
    "profile_picture": null,
    "followers_count": 2,
    "following_count": 5,
    "created_at": "2026-02-21T10:30:00Z",
    "updated_at": "2026-02-21T10:30:00Z"
  }
}
```

### 3. User Profile - Retrieve
- **URL**: `/api/auth/profile/`
- **Method**: `GET`
- **Authentication**: Required (Token)
- **Headers**:
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbea6f3ba4
```
- **Response** (200 OK):
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "bio": "Welcome to my profile",
  "profile_picture": null,
  "followers_count": 2,
  "following_count": 5,
  "created_at": "2026-02-21T10:30:00Z",
  "updated_at": "2026-02-21T10:30:00Z"
}
```

### 4. User Profile - Update
- **URL**: `/api/auth/profile/`
- **Method**: `PATCH` or `PUT`
- **Authentication**: Required (Token)
- **Headers**:
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbea6f3ba4
Content-Type: application/json
```
- **Request Body** (PATCH - only fields to update):
```json
{
  "first_name": "Jonathan",
  "bio": "Updated bio text"
}
```
- **Response** (200 OK):
```json
{
  "message": "Profile updated successfully",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "Jonathan",
    "last_name": "Doe",
    "bio": "Updated bio text",
    "profile_picture": null,
    "followers_count": 2,
    "following_count": 5,
    "created_at": "2026-02-21T10:30:00Z",
    "updated_at": "2026-02-21T10:31:00Z"
  }
}
```

### 5. User Logout
- **URL**: `/api/auth/logout/`
- **Method**: `POST`
- **Authentication**: Required (Token)
- **Headers**:
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbea6f3ba4
```
- **Response** (200 OK):
```json
{
  "message": "Logout successful"
}
```

### 6. Get User Details by ID
- **URL**: `/api/auth/users/<user_id>/`
- **Method**: `GET`
- **Authentication**: Required (Token)
- **Example**: `/api/auth/users/1/`
- **Headers**:
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbea6f3ba4
```
- **Response** (200 OK):
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "bio": "Welcome to my profile",
  "profile_picture": null,
  "followers_count": 2,
  "following_count": 5,
  "created_at": "2026-02-21T10:30:00Z",
  "updated_at": "2026-02-21T10:31:00Z"
}
```

### 7. List All Users
- **URL**: `/api/auth/users/`
- **Method**: `GET`
- **Authentication**: Required (Token)
- **Headers**:
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbea6f3ba4
```
- **Response** (200 OK):
```json
[
  {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "bio": "Welcome to my profile",
    "profile_picture": null,
    "followers_count": 2,
    "following_count": 5,
    "created_at": "2026-02-21T10:30:00Z",
    "updated_at": "2026-02-21T10:31:00Z"
  },
  {
    "id": 2,
    "username": "janedoe",
    "email": "jane@example.com",
    "first_name": "Jane",
    "last_name": "Doe",
    "bio": "Jane's bio",
    "profile_picture": null,
    "followers_count": 5,
    "following_count": 3,
    "created_at": "2026-02-21T10:35:00Z",
    "updated_at": "2026-02-21T10:36:00Z"
  }
]
```

## Authentication Methods

### Token Authentication
All protected endpoints use **Token Authentication** from Django REST Framework.

**How to use:**
1. Register or login to obtain a token
2. Include the token in the `Authorization` header of subsequent requests:
```
Authorization: Token <your_token_here>
```

## Error Responses

### 400 Bad Request - Validation Error
```json
{
  "password": [
    "Passwords do not match."
  ]
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

## Summary

✅ **URL Configuration Complete**
- Registration (`/register/`) - Returns token on success
- Login (`/login/`) - Returns token on success
- Profile Management (`/profile/`) - Get/Update authenticated user
- User Details (`/users/<id>/`) - View specific user
- Users List (`/users/`) - List all users
- Logout (`/logout/`) - Invalidate token

All endpoints are properly integrated with token authentication.
